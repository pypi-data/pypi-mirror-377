"""Idempotency middleware for preventing duplicate message processing."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Set, Callable, Union
from .base import Middleware

logger = logging.getLogger(__name__)


class IdempotencyStore:
    """Abstract base class for idempotency storage backends."""

    async def get(
        self, key: str, consistent_read: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a record by key.
        
        Args:
            key: Idempotency key
            consistent_read: Whether to use consistent read
            
        Returns:
            Record data if found, None otherwise
        """
        raise NotImplementedError

    async def put(
        self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> None:
        """Store a record.
        
        Args:
            key: Idempotency key
            value: Record data
            ttl_seconds: Optional TTL in seconds
        """
        raise NotImplementedError

    async def conditional_put(
        self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store a record only if key doesn't exist.
        
        Args:
            key: Idempotency key
            value: Record data
            ttl_seconds: Optional TTL in seconds
            
        Returns:
            True if stored, False if key already exists
        """
        raise NotImplementedError

    async def update(self, key: str, updates: Dict[str, Any]) -> bool:
        """Update an existing record.
        
        Args:
            key: Idempotency key
            updates: Fields to update
            
        Returns:
            True if updated, False if key doesn't exist
        """
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        """Delete a record.
        
        Args:
            key: Idempotency key
        """
        raise NotImplementedError

    async def conditional_delete(
        self, key: str, condition_attr: str, condition_value: Any
    ) -> bool:
        """Delete a record conditionally.
        
        Args:
            key: Idempotency key
            condition_attr: Attribute to check
            condition_value: Expected value
            
        Returns:
            True if deleted, False if condition not met
        """
        raise NotImplementedError


class MemoryIdempotencyStore(IdempotencyStore):
    """In-memory implementation of idempotency store.
    
    Suitable for testing and single-instance deployments.
    Records are lost when the process restarts.
    """

    def __init__(self):
        """Initialize memory store."""
        self._store: Dict[str, Dict[str, Any]] = {}

    async def get(
        self, key: str, consistent_read: bool = False
    ) -> Optional[Dict[str, Any]]:
        record = self._store.get(key)
        if record and record.get("expires_at", float("inf")) > time.time():
            return record
        elif record:
            del self._store[key]
        return None

    async def put(
        self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> None:
        if ttl_seconds:
            value["expires_at"] = time.time() + ttl_seconds
        self._store[key] = value

    async def conditional_put(
        self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> bool:
        if key in self._store:
            record = self._store[key]
            if record.get("expires_at", float("inf")) > time.time():
                return False
            else:
                del self._store[key]

        await self.put(key, value, ttl_seconds)
        return True

    async def update(self, key: str, updates: Dict[str, Any]) -> bool:
        if key not in self._store:
            return False

        record = self._store[key]
        if record.get("expires_at", float("inf")) <= time.time():
            del self._store[key]
            return False

        record.update(updates)
        return True

    async def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

    async def conditional_delete(
        self, key: str, condition_attr: str, condition_value: Any
    ) -> bool:
        if (
            key in self._store
            and self._store[key].get(condition_attr) == condition_value
        ):
            del self._store[key]
            return True
        return False


class DynamoDBIdempotencyStore(IdempotencyStore):
    """DynamoDB implementation of idempotency store.
    
    Provides persistent, scalable idempotency storage using DynamoDB
    with automatic table creation and TTL configuration.
    """

    def __init__(
        self,
        table_name: str,
        key_attr: str = "idempotency_key",
        ttl_attr: str = "ttl",
        region_name: Optional[str] = None,
        create_table: bool = True,
        read_capacity_units: int = 5,
        write_capacity_units: int = 5,
    ):
        """Initialize DynamoDB store.
        
        Args:
            table_name: DynamoDB table name
            key_attr: Attribute name for the primary key
            ttl_attr: Attribute name for TTL
            region_name: AWS region name
            create_table: Whether to create table if it doesn't exist
            read_capacity_units: Read capacity for table creation
            write_capacity_units: Write capacity for table creation
            
        Raises:
            ImportError: If aioboto3 is not installed
        """
        try:
            import aioboto3
            from botocore.exceptions import ClientError
            from boto3.dynamodb.conditions import Attr

            self.ClientError = ClientError
            self.Attr = Attr
            self.session = aioboto3.Session()
            self.table_name = table_name
            self.region_name = region_name
            self.key_attr = key_attr
            self.ttl_attr = ttl_attr
            self.create_table = create_table
            self.read_capacity_units = read_capacity_units
            self.write_capacity_units = write_capacity_units
            self._table = None
            self._table_exists_checked = False
        except ImportError:
            raise ImportError("aioboto3 is required for DynamoDB idempotency store")

    async def _ensure_table_exists(self):
        if not self.create_table or self._table_exists_checked:
            return

        try:
            async with self.session.resource(
                "dynamodb", region_name=self.region_name
            ) as dynamodb:
                try:
                    table = await dynamodb.Table(self.table_name)
                    await table.load()
                    logger.info(f"DynamoDB table {self.table_name} already exists")

                    await self._ensure_ttl_enabled(table)

                except self.ClientError as e:
                    if e.response["Error"]["Code"] == "ResourceNotFoundException":
                        await self._create_table(dynamodb)
                    else:
                        raise

                self._table_exists_checked = True

        except Exception as e:
            logger.error(f"Failed to ensure table exists: {str(e)}")
            raise

    async def _create_table(self, dynamodb):
        try:
            logger.info(f"Creating DynamoDB table {self.table_name}")

            table = await dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[{"AttributeName": self.key_attr, "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": self.key_attr, "AttributeType": "S"}
                ],
                BillingMode="PROVISIONED",
                ProvisionedThroughput={
                    "ReadCapacityUnits": self.read_capacity_units,
                    "WriteCapacityUnits": self.write_capacity_units,
                },
            )

            await table.wait_until_exists()
            logger.info(f"DynamoDB table {self.table_name} created successfully")

            await self._ensure_ttl_enabled(table)

        except self.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                logger.info(f"Table {self.table_name} already exists")
            else:
                logger.error(f"Failed to create table {self.table_name}: {str(e)}")
                raise

    async def _ensure_ttl_enabled(self, table):
        try:
            async with self.session.client(
                "dynamodb", region_name=self.region_name
            ) as client:
                try:
                    response = await client.describe_time_to_live(
                        TableName=self.table_name
                    )
                    ttl_status = response.get("TimeToLiveDescription", {}).get(
                        "TimeToLiveStatus"
                    )

                    if ttl_status != "ENABLED":
                        logger.info(f"Enabling TTL on table {self.table_name}")
                        await client.update_time_to_live(
                            TableName=self.table_name,
                            TimeToLiveSpecification={
                                "AttributeName": self.ttl_attr,
                                "Enabled": True,
                            },
                        )
                        logger.info(f"TTL enabled on table {self.table_name}")
                    else:
                        logger.debug(f"TTL already enabled on table {self.table_name}")

                except self.ClientError as e:
                    if e.response["Error"]["Code"] != "ValidationException":
                        logger.warning(
                            f"Failed to enable TTL on table {self.table_name}: {str(e)}"
                        )

        except Exception as e:
            logger.warning(
                f"Failed to configure TTL on table {self.table_name}: {str(e)}"
            )

    async def _get_table(self):
        if self._table is None:
            await self._ensure_table_exists()
            async with self.session.resource(
                "dynamodb", region_name=self.region_name
            ) as dynamodb:
                self._table = await dynamodb.Table(self.table_name)
        return self._table

    async def get(
        self, key: str, consistent_read: bool = False
    ) -> Optional[Dict[str, Any]]:
        try:
            await self._ensure_table_exists()
            async with self.session.resource(
                "dynamodb", region_name=self.region_name
            ) as dynamodb:
                table = await dynamodb.Table(self.table_name)
                response = await table.get_item(
                    Key={self.key_attr: key}, ConsistentRead=consistent_read
                )
                item = response.get("Item")
                if item:
                    item.pop(self.key_attr, None)
                    item.pop(self.ttl_attr, None)
                    return item
        except Exception:
            pass
        return None

    async def put(
        self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> None:
        item = {self.key_attr: key, **value}
        if ttl_seconds:
            item[self.ttl_attr] = int(time.time() + ttl_seconds)

        try:
            await self._ensure_table_exists()
            async with self.session.resource(
                "dynamodb", region_name=self.region_name
            ) as dynamodb:
                table = await dynamodb.Table(self.table_name)
                await table.put_item(Item=item)
        except Exception:
            pass

    async def conditional_put(
        self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> bool:
        item = {self.key_attr: key, **value}
        if ttl_seconds:
            item[self.ttl_attr] = int(time.time() + ttl_seconds)

        try:
            current_time = int(time.time())
            await self._ensure_table_exists()

            async with self.session.resource(
                "dynamodb", region_name=self.region_name
            ) as dynamodb:
                table = await dynamodb.Table(self.table_name)
                await table.put_item(
                    Item=item,
                    ConditionExpression=f"attribute_not_exists(#{self.key_attr}) OR #{self.ttl_attr} <= :now",
                    ExpressionAttributeNames={
                        f"#{self.key_attr}": self.key_attr,
                        f"#{self.ttl_attr}": self.ttl_attr,
                    },
                    ExpressionAttributeValues={":now": current_time},
                )
            return True
        except self.ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise

    async def _update_with_retry(self, key: str, updates: Dict[str, Any], max_retries: int = 3) -> bool:
        """Update with exponential backoff retry for transient errors."""
        for attempt in range(max_retries):
            try:
                update_expression_parts = []
                expression_attribute_values = {}

                for k, v in updates.items():
                    update_expression_parts.append(f"#{k} = :{k}")
                    expression_attribute_values[f":{k}"] = v

                expression_attribute_names = {f"#{k}": k for k in updates.keys()}
                expression_attribute_names[f"#{self.key_attr}"] = self.key_attr

                await self._ensure_table_exists()
                async with self.session.resource(
                    "dynamodb", region_name=self.region_name
                ) as dynamodb:
                    table = await dynamodb.Table(self.table_name)
                    await table.update_item(
                        Key={self.key_attr: key},
                        UpdateExpression="SET " + ", ".join(update_expression_parts),
                        ExpressionAttributeNames=expression_attribute_names,
                        ExpressionAttributeValues=expression_attribute_values,
                        ConditionExpression=f"attribute_exists(#{self.key_attr})",
                    )
                return True
            except self.ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "ConditionalCheckFailedException":
                    logger.warning(f"DynamoDB update failed: Record {key} does not exist")
                    return False
                elif error_code in ["ProvisionedThroughputExceededException", "ThrottlingException", "ServiceUnavailable"]:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 0.1  # Exponential backoff: 0.1s, 0.2s, 0.4s
                        logger.warning(f"DynamoDB transient error for key {key} (attempt {attempt + 1}/{max_retries}): {error_code}, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                logger.error(f"DynamoDB update failed for key {key}: {error_code} - {e.response['Error']['Message']}")
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 0.1
                    logger.warning(f"DynamoDB update error for key {key} (attempt {attempt + 1}/{max_retries}): {type(e).__name__}: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                logger.error(f"DynamoDB update failed for key {key}: {type(e).__name__}: {e}")
                raise
        return False

    async def update(self, key: str, updates: Dict[str, Any]) -> bool:
        return await self._update_with_retry(key, updates)

    async def delete(self, key: str) -> None:
        try:
            await self._ensure_table_exists()
            async with self.session.resource(
                "dynamodb", region_name=self.region_name
            ) as dynamodb:
                table = await dynamodb.Table(self.table_name)
                await table.delete_item(Key={self.key_attr: key})
        except Exception:
            pass

    async def conditional_delete(
        self, key: str, condition_attr: str, condition_value: Any
    ) -> bool:
        try:
            await self._ensure_table_exists()
            async with self.session.resource(
                "dynamodb", region_name=self.region_name
            ) as dynamodb:
                table = await dynamodb.Table(self.table_name)
                await table.delete_item(
                    Key={self.key_attr: key},
                    ConditionExpression=self.Attr(condition_attr).eq(condition_value),
                )
            return True
        except self.ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            logger.warning(f"Error in conditional delete for {key}: {e}")
            return False
        except Exception as e:
            logger.warning(f"Error in conditional delete for {key}: {e}")
            return False


class IdempotencyMiddleware(Middleware):
    """Middleware that prevents duplicate processing of messages.
    
    Uses configurable storage backend to track processed messages
    and prevent duplicate execution with support for strong consistency
    and per-entity sequencing.
    """

    def __init__(
        self,
        store: Optional[IdempotencyStore] = None,
        key_generator: Optional[Callable[[dict, dict], str]] = None,
        ttl_seconds: int = 3600,
        skip_on_error: bool = False,
        use_message_deduplication_id: bool = False,
        payload_hash_fields: Optional[list] = None,
        use_strong_consistency: bool = True,
        per_entity_sequencing: bool = False,
        entity_key_extractor: Optional[Callable[[dict], str]] = None,
        fail_on_store_errors: bool = True,
        entity_lock_ttl_seconds: Optional[int] = None,
        sqs_visibility_timeout_seconds: int = 30,
    ):
        """Initialize idempotency middleware.
        
        Args:
            store: Storage backend for idempotency records
            key_generator: Function to generate idempotency keys
            ttl_seconds: TTL for idempotency records
            skip_on_error: Whether to skip idempotency on store errors
            use_message_deduplication_id: Use SQS deduplication ID as key
            payload_hash_fields: Specific fields to hash for key generation
            use_strong_consistency: Enable strong consistency mode
            per_entity_sequencing: Enable per-entity sequencing
            entity_key_extractor: Function to extract entity keys
            fail_on_store_errors: Whether to fail on store errors
            entity_lock_ttl_seconds: TTL for entity locks
            sqs_visibility_timeout_seconds: SQS visibility timeout
        """
        super().__init__()
        self.store = store or MemoryIdempotencyStore()
        self.key_generator = key_generator or self._default_key_generator
        self.ttl_seconds = ttl_seconds
        self.skip_on_error = skip_on_error
        self.use_message_deduplication_id = use_message_deduplication_id
        self.payload_hash_fields = payload_hash_fields or []
        self.use_strong_consistency = use_strong_consistency
        self.per_entity_sequencing = per_entity_sequencing
        self.entity_key_extractor = entity_key_extractor
        self.fail_on_store_errors = fail_on_store_errors

        self.entity_lock_ttl_seconds = entity_lock_ttl_seconds or (
            sqs_visibility_timeout_seconds + 60
        )
        self.sqs_visibility_timeout_seconds = sqs_visibility_timeout_seconds

    def _default_key_generator(self, payload: dict, record: dict) -> str:
        if self.use_message_deduplication_id:
            attributes = record.get("attributes", {})
            dedup_id = attributes.get("messageDeduplicationId")
            if dedup_id:
                return f"dedup:{dedup_id}"

        return self._hash_payload(payload)

    def _hash_payload(self, payload: dict) -> str:
        if self.payload_hash_fields:
            hash_data = {
                k: payload.get(k) for k in self.payload_hash_fields if k in payload
            }
        else:
            hash_data = payload

        payload_str = json.dumps(hash_data, sort_keys=True, separators=(",", ":"))
        return f"hash:{hashlib.sha256(payload_str.encode()).hexdigest()}"

    def _get_entity_key(self, payload: dict) -> Optional[str]:
        if not self.per_entity_sequencing or not self.entity_key_extractor:
            return None
        return self.entity_key_extractor(payload)

    async def _acquire_entity_lock(self, entity_key: str, idempotency_key: str) -> bool:
        lock_key = f"lock:{entity_key}"
        lock_record = {
            "status": "LOCKED",
            "locked_by": idempotency_key,
            "created_at": int(time.time()),
        }

        try:
            return await self.store.conditional_put(
                lock_key, lock_record, self.entity_lock_ttl_seconds
            )
        except Exception as e:
            if self.fail_on_store_errors:
                raise IdempotencyStoreError(f"Failed to acquire entity lock: {str(e)}")
            return False

    async def _release_entity_lock(self, entity_key: str, idempotency_key: str) -> None:
        lock_key = f"lock:{entity_key}"
        try:
            if hasattr(self.store, "conditional_delete"):
                success = await self.store.conditional_delete(
                    lock_key, "locked_by", idempotency_key
                )
                if not success:
                    logger.warning(
                        f"Failed to release lock {lock_key}: not owned by {idempotency_key}"
                    )
            else:
                await self.store.delete(lock_key)
        except Exception as e:
            if self.fail_on_store_errors:
                raise IdempotencyStoreError(f"Failed to release entity lock: {str(e)}")

    async def before(
        self, payload: dict, record: dict, context: Any, ctx: dict
    ) -> None:
        msg_id = record.get("messageId", "UNKNOWN")

        try:
            idempotency_key = self.key_generator(payload, record)
            ctx["idempotency_key"] = idempotency_key
            self._log(
                "debug",
                f"Generated idempotency key",
                msg_id=msg_id,
                idempotency_key=idempotency_key,
            )

            entity_key = (
                self._get_entity_key(payload) if self.per_entity_sequencing else None
            )
            if entity_key:
                ctx["entity_key"] = entity_key
                self._log("debug", f"Entity key", msg_id=msg_id, entity_key=entity_key)

            if self.use_strong_consistency:
                self._log("debug", f"Using strong consistency mode", msg_id=msg_id)
                reservation_record = {
                    "status": "IN_PROGRESS",
                    "created_at": int(time.time()),
                    "message_id": record.get("messageId"),
                    "entity_key": entity_key,
                }

                self._log("debug", f"Attempting to create reservation", msg_id=msg_id)
                success = await self.store.conditional_put(
                    idempotency_key, reservation_record, self.ttl_seconds
                )

                if not success:
                    self._log(
                        "debug",
                        f"Reservation failed, checking existing record",
                        msg_id=msg_id,
                    )
                    existing_record = await self.store.get(
                        idempotency_key, consistent_read=True
                    )
                    if existing_record:
                        status = existing_record.get("status")
                        self._log(
                            "debug",
                            f"Found existing record",
                            msg_id=msg_id,
                            status=status,
                        )

                        if status == "IN_PROGRESS":
                            self._log(
                                "info",
                                f"Message is currently in progress",
                                msg_id=msg_id,
                            )
                            raise IdempotencyInProgress(
                                key=idempotency_key,
                                created_at=existing_record.get("created_at"),
                            )
                        elif status == "COMPLETED":
                            self._log(
                                "info",
                                f"Message already completed, returning cached result",
                                msg_id=msg_id,
                            )
                            ctx["idempotency_hit"] = True
                            ctx["idempotency_result"] = existing_record.get("result")
                            ctx["idempotency_timestamp"] = existing_record.get(
                                "finished_at"
                            )

                            raise IdempotencyHit(
                                key=idempotency_key,
                                result=existing_record.get("result"),
                                timestamp=existing_record.get("finished_at"),
                            )
                        elif status == "FAILED":
                            self._log(
                                "warning", f"Message failed previously", msg_id=msg_id
                            )
                            raise IdempotencyFailedPreviously(
                                key=idempotency_key,
                                error=existing_record.get("error"),
                                timestamp=existing_record.get("finished_at"),
                            )
                    else:
                        self._log(
                            "warning",
                            f"No existing record found despite conditional_put failure",
                            msg_id=msg_id,
                        )
                else:
                    self._log(
                        "debug", f"Reservation created successfully", msg_id=msg_id
                    )

                if entity_key:
                    self._log(
                        "debug", f"Attempting to acquire entity lock", msg_id=msg_id
                    )
                    if not await self._acquire_entity_lock(entity_key, idempotency_key):
                        self._log(
                            "warning",
                            f"Failed to acquire entity lock, cleaning up",
                            msg_id=msg_id,
                        )
                        try:
                            await self.store.delete(idempotency_key)
                        except Exception:
                            pass

                        raise EntityLockAcquisitionFailed(
                            entity_key=entity_key, idempotency_key=idempotency_key
                        )
                    self._log("debug", f"Entity lock acquired", msg_id=msg_id)
                    ctx["entity_locked"] = True

                ctx["idempotency_hit"] = False
                ctx["reservation_created"] = True
            else:
                self._log("debug", f"Using eventual consistency mode", msg_id=msg_id)
                existing_record = await self.store.get(idempotency_key)
                if existing_record:
                    self._log(
                        "info",
                        f"Found existing record, returning cached result",
                        msg_id=msg_id,
                    )
                    ctx["idempotency_hit"] = True
                    ctx["idempotency_result"] = existing_record.get("result")
                    ctx["idempotency_timestamp"] = existing_record.get("timestamp")

                    raise IdempotencyHit(
                        key=idempotency_key,
                        result=existing_record.get("result"),
                        timestamp=existing_record.get("timestamp"),
                    )
                else:
                    self._log(
                        "debug",
                        f"No existing record found, proceeding with processing",
                        msg_id=msg_id,
                    )
                    ctx["idempotency_hit"] = False

        except (
            IdempotencyHit,
            IdempotencyInProgress,
            IdempotencyFailedPreviously,
            EntityLockAcquisitionFailed,
        ):
            raise
        except Exception as e:
            self._log(
                "error",
                f"Error during idempotency check",
                msg_id=msg_id,
                error_type=type(e).__name__,
                error=str(e),
            )
            if self.fail_on_store_errors or not self.skip_on_error:
                raise IdempotencyStoreError(f"Idempotency check failed: {str(e)}")
            ctx["idempotency_error"] = str(e)

    async def after(
        self,
        payload: dict,
        record: dict,
        context: Any,
        ctx: dict,
        error: Optional[Exception],
    ) -> None:
        entity_key = ctx.get("entity_key")
        idempotency_key = ctx.get("idempotency_key")
        msg_id = record.get("messageId", "UNKNOWN")

        try:
            if ctx.get("idempotency_hit") or not ctx.get("reservation_created"):
                self._log(
                    "debug",
                    f"Skipping after processing",
                    msg_id=msg_id,
                    hit=ctx.get("idempotency_hit"),
                    reservation=ctx.get("reservation_created"),
                )
                return

            if self.use_strong_consistency and idempotency_key:
                if error:
                    self._log(
                        "debug", f"Updating record with failure status", msg_id=msg_id
                    )
                    failure_record = {
                        "status": "FAILED",
                        "finished_at": int(time.time()),
                        "error": str(error),
                        "error_type": type(error).__name__,
                    }
                    update_success = await self.store.update(idempotency_key, failure_record)
                    if not update_success:
                        self._log(
                            "warning",
                            f"Failed to update idempotency record to FAILED status - record may not exist, attempting cleanup",
                            msg_id=msg_id,
                            idempotency_key=idempotency_key,
                        )
                        # Attempt to delete the record to prevent it from staying IN_PROGRESS
                        try:
                            await self.store.delete(idempotency_key)
                            self._log(
                                "info",
                                f"Deleted stuck idempotency record",
                                msg_id=msg_id,
                                idempotency_key=idempotency_key,
                            )
                        except Exception as delete_error:
                            self._log(
                                "error",
                                f"Failed to delete stuck idempotency record",
                                msg_id=msg_id,
                                idempotency_key=idempotency_key,
                                error=str(delete_error),
                            )
                else:
                    self._log(
                        "debug",
                        f"Updating record with completion status",
                        msg_id=msg_id,
                    )
                    completion_record = {
                        "status": "COMPLETED",
                        "finished_at": int(time.time()),
                        "result": ctx.get("handler_result"),
                    }
                    update_success = await self.store.update(idempotency_key, completion_record)
                    if not update_success:
                        self._log(
                            "warning",
                            f"Failed to update idempotency record to COMPLETED status - record may not exist, attempting cleanup",
                            msg_id=msg_id,
                            idempotency_key=idempotency_key,
                        )
                        # Attempt to delete the record to prevent it from staying IN_PROGRESS
                        try:
                            await self.store.delete(idempotency_key)
                            self._log(
                                "info",
                                f"Deleted stuck idempotency record",
                                msg_id=msg_id,
                                idempotency_key=idempotency_key,
                            )
                        except Exception as delete_error:
                            self._log(
                                "error",
                                f"Failed to delete stuck idempotency record",
                                msg_id=msg_id,
                                idempotency_key=idempotency_key,
                                error=str(delete_error),
                            )
            elif not error and idempotency_key:
                self._log(
                    "debug",
                    f"Storing idempotency record for successful processing",
                    msg_id=msg_id,
                )
                idempotency_record = {
                    "timestamp": int(time.time()),
                    "message_id": record.get("messageId"),
                    "result": ctx.get("handler_result"),
                    "status": "completed",
                }

                await self.store.put(
                    idempotency_key, idempotency_record, self.ttl_seconds
                )

            if ctx.get("entity_locked") and entity_key and idempotency_key:
                print(f"[IDEMPOTENCY] {msg_id} - Releasing entity lock")
                await self._release_entity_lock(entity_key, idempotency_key)

        except Exception as e:
            print(
                f"[IDEMPOTENCY] {msg_id} - Error during after processing: {type(e).__name__}: {e}"
            )
            if ctx.get("entity_locked") and entity_key and idempotency_key:
                try:
                    print(
                        f"[IDEMPOTENCY] {msg_id} - Attempting to release entity lock after error"
                    )
                    await self._release_entity_lock(entity_key, idempotency_key)
                except Exception as lock_error:
                    print(
                        f"[IDEMPOTENCY] {msg_id} - Failed to release entity lock: {lock_error}"
                    )

            if self.fail_on_store_errors or not self.skip_on_error:
                raise IdempotencyStoreError(
                    f"Failed to update idempotency record: {str(e)}"
                )
            ctx["idempotency_store_error"] = str(e)


class IdempotencyHit(Exception):
    """Exception raised when a message has already been processed."""

    def __init__(self, key: str, result: Any = None, timestamp: Optional[float] = None):
        """Initialize idempotency hit exception.
        
        Args:
            key: Idempotency key that was hit
            result: Cached result from previous processing
            timestamp: Timestamp of previous processing
        """
        self.key = key
        self.result = result
        self.timestamp = timestamp
        super().__init__(f"Message already processed: {key}")


class IdempotencyInProgress(Exception):
    """Exception raised when a message is currently being processed."""

    def __init__(self, key: str, created_at: Optional[float] = None):
        """Initialize in-progress exception.
        
        Args:
            key: Idempotency key that is in progress
            created_at: Timestamp when processing started
        """
        self.key = key
        self.created_at = created_at
        super().__init__(f"Message currently in progress: {key}")


class IdempotencyFailedPreviously(Exception):
    """Exception raised when a message failed processing previously."""

    def __init__(self, key: str, error: Any = None, timestamp: Optional[float] = None):
        """Initialize failed-previously exception.
        
        Args:
            key: Idempotency key that failed previously
            error: Previous error details
            timestamp: Timestamp of previous failure
        """
        self.key = key
        self.error = error
        self.timestamp = timestamp
        super().__init__(f"Message failed previously: {key}, error: {error}")


class EntityLockAcquisitionFailed(Exception):
    """Exception raised when entity lock acquisition fails."""

    def __init__(self, entity_key: str, idempotency_key: str):
        """Initialize lock acquisition failure exception.
        
        Args:
            entity_key: Entity key that couldn't be locked
            idempotency_key: Idempotency key attempting the lock
        """
        self.entity_key = entity_key
        self.idempotency_key = idempotency_key
        super().__init__(f"Failed to acquire lock for entity: {entity_key}")


class IdempotencyStoreError(Exception):
    """Exception raised when idempotency store operations fail."""

    def __init__(self, message: str):
        """Initialize store error exception.
        
        Args:
            message: Error message
        """
        self.message = message
        super().__init__(message)
