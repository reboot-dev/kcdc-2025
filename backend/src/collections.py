import google.protobuf.any_pb2
from dataclasses import dataclass
from resemble.aio.contexts import TransactionContext, WorkflowContext
from resemble.aio.types import StateId
from resemble.aio.workflows import Workflow
from list.v1 import list_rsm
from typing import Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')


@dataclass(kw_only=True)
class Page(Generic[U]):

    items: list[U]


class List(Generic[T]):


    class WeakReference(Generic[U]):

        def __init__(self, id: StateId, u: type[U]):
            self._weak_reference = list_rsm.List.ref(id)
            self._u = u

        async def Append(
            self,
            context_or_workflow: TransactionContext | WorkflowContext | Workflow,
            *,
            item: U,
        ):        
            return await self._weak_reference.Append(
                context_or_workflow,
                item=self._wrap(item),
            )

        async def Remove(
            self,
            context_or_workflow: TransactionContext | WorkflowContext | Workflow,
            *,
            item: U,
        ):
            return await self._weak_reference.Remove(
                context_or_workflow,
                item=self._wrap(item),
            )

        async def GetPage(
            self,
            context_or_workflow: TransactionContext | WorkflowContext | Workflow,
            *,
            page: int,
            items_per_page: int,
        ) -> Page[U]:
            page = await self._weak_reference.GetPage(
                context_or_workflow,
                page=page,
                items_per_page=items_per_page,
            )

            return Page(
                items=[self._unwrap(item) for item in page.items],
            )

        def _wrap(self, item: U):
            assert self._u == type(item)
            if self._u == float:
                return list_rsm.Item(as_double=item)
            elif self._u == int:
                return list_rsm.Item(as_int64=item)
            elif self._u == bool:
                return list_rsm.Item(as_bool=item)
            elif self._u == str:
                return list_rsm.Item(as_string=item)
            elif self._u == bytes:
                return list_rsm.Item(as_bytes=item)
            else:
                any = google.protobuf.any_pb2.Any()
                any.Pack(item)
                return list_rsm.Item(as_any=any)

        def _unwrap(self, item: list_rsm.Item):
            if self._u == float:
                return item.as_double
            elif self._u == int:
                return item.as_int64
            elif self._u == bool:
                return item.as_bool
            elif self._u == str:
                return item.as_string
            elif self._u == bytes:
                return item.as_bytes
            else:
                u = self._u()
                item.as_any.Unpack(u)
                return u

    def __init__(self, t: type[T]):
        self.t = t

    def ref(self, id: str) -> WeakReference[T]:
        return List.WeakReference(id, self.t)