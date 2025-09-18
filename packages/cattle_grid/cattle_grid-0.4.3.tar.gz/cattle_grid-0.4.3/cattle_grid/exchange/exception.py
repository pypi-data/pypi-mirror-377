from faststream.rabbit import RabbitBroker
from faststream import ExceptionMiddleware, Context

import logging
import json

from cattle_grid.account.account import account_for_actor
from cattle_grid.model.account import ErrorMessage
from cattle_grid.dependencies import CorrelationId, AccountExchange, SqlSession
from cattle_grid.dependencies.processing import RoutingKey

logger = logging.getLogger(__name__)

exception_middleware = ExceptionMiddleware()


@exception_middleware.add_handler(Exception)
async def exception_handler(
    exception: Exception,
    routing_key: RoutingKey,
    correlation_id: CorrelationId,
    session: SqlSession,
    account_exchange: AccountExchange,
    message=Context("message.body"),
    broker: RabbitBroker = Context(),
):
    try:
        data = json.loads(message)
        actor_id = data["actor"]
    except Exception:
        logger.exception(exception)
        logger.exception(message)
        return

    logger.info("Exception for %s", actor_id)

    account = await account_for_actor(session, actor_id)
    if not account:
        return
    name = account.name

    logger.error("Processing error occurred in exchange for account %s", name)

    await broker.publish(
        ErrorMessage(message=str(exception), routing_key=routing_key),
        routing_key=f"error.{name}",
        exchange=account_exchange,
        correlation_id=correlation_id,
    )
