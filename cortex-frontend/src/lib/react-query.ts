import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1, // 失败重试次数
            refetchOnWindowFocus: false, // 窗口聚焦时不自动刷新，防止开发时闪烁
        }
    }
});