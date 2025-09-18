from faststream import Context
from faststream.rabbit import RabbitBroker

from cattle_grid.account.account import group_names_for_actor
from cattle_grid.model.account import TriggerMessage
from cattle_grid.dependencies.globals import global_container
from cattle_grid.dependencies import CorrelationId, RewriteRules, SqlSession

from .annotations import ActorForAccountFromMessage, MethodFromRoutingKey


async def handle_trigger(
    msg: TriggerMessage,
    actor: ActorForAccountFromMessage,
    correlation_id: CorrelationId,
    method: MethodFromRoutingKey,
    session: SqlSession,
    rewrite_rules: RewriteRules,
    broker: RabbitBroker = Context(),
):
    """Used to trigger a method performed by the actor.

    The main thing an actor can do is send activities to
    the Fediverse. This can be done with `send_message`.
    This can be extended in cattle_grid through extensions.

    However the methods to update the actor profile and delete
    the actor are also called via a trigger.
    """

    if rewrite_rules:
        group_names = await group_names_for_actor(session, actor)
        method = rewrite_rules.rewrite(method, group_names)

    await broker.publish(
        msg,
        routing_key=method,
        exchange=global_container.exchange,
        correlation_id=correlation_id,
    )
