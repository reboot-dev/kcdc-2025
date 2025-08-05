from list.v1.list_rbt import (
    AppendRequest,
    AppendResponse,
    GetPageRequest,
    GetPageResponse,
    List,
    ListState,
    RemoveResponse,
    RemoveRequest,
)
from rebootdev.aio.contexts import ReaderContext, WriterContext


class ListServicer(List.alpha.Servicer):

    async def Append(
        self,
        context: WriterContext,
        request: AppendRequest,
    ) -> AppendResponse:
        self.state.items.append(request.item)
        return AppendResponse()

    async def Remove(
        self,
        context: WriterContext,
        request: RemoveRequest,
    ) -> RemoveResponse:
        serialized_item = request.item.SerializeToString(deterministic=True)

        for i in range(len(self.state.items)):
            if (self.state.items[i].SerializeToString(
                    deterministic=True) == serialized_item):
                items = self.state.items[:i] + self.state.items[i + 1:]
                del self.state.items[:]
                self.state.items.extend(items)
                break

        return RemoveResponse()

    def _page_offsets(
        self,
        *,
        page: int,
        items: int,
        items_per_page: int,
    ):
        begin: int
        end: int

        if page >= 0:
            begin = page * items_per_page
            end = min(begin + items_per_page, items)
        else:
            page = -page - 1
            end = items - (page * items_per_page)
            begin = max(end - items_per_page, 0)

        return (begin, end)

    async def GetPage(
        self,
        context: ReaderContext,
        request: GetPageRequest,
    ):
        begin, end = self._page_offsets(
            page=request.page,
            items=len(self.state.items),
            items_per_page=request.items_per_page,
        )

        return GetPageResponse(items=self.state.items[begin:end])
