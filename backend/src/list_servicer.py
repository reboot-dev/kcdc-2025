from list.v1.list_rsm import (
    AppendRequest,
    AppendResponse,
    GetPageRequest,
    GetPageResponse,
    List,
    ListState,
    RemoveResponse,
    RemoveRequest,
)
from resemble.aio.contexts import ReaderContext, WriterContext


class ListServicer(List.Interface):

    async def Append(
        self,
        context: WriterContext,
        state: ListState,
        request: AppendRequest,
    ):
        state.items.append(request.item)
        return List.AppendEffects(
            state=state,
            response=AppendResponse(),
        )

    async def Remove(
        self,
        context: WriterContext,
        state: ListState,
        request: RemoveRequest,
    ):
        serialized_item = request.item.SerializeToString(deterministic=True)

        for i in range(len(state.items)):
            if (
                state.items[i].SerializeToString(deterministic=True) ==
                serialized_item
            ):
                items = state.items[:i] + state.items[i+1:]
                del state.items[:]
                state.items.extend(items)
                break

        return List.RemoveEffects(
            state=state,
            response=RemoveResponse(),
        )

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
        state: ListState,
        request: GetPageRequest,
    ):
        begin, end = self._page_offsets(
            page=request.page,
            items=len(state.items),
            items_per_page=request.items_per_page,
        )

        return GetPageResponse(items=state.items[begin:end])