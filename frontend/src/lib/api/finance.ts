import { api } from "./client";

export interface Account {
  id: string;
  code: string;
  name: string;
  account_type: string;
  balance: number;
  currency: string;
  is_active: boolean;
}

export const financeApi = {
  listAccounts: (token: string) => api.get<Account[]>("/api/v1/finance/accounts", { token }),
  createAccount: (token: string, data: Partial<Account> & { code: string; name: string; account_type: string }) =>
    api.post<Account>("/api/v1/finance/accounts", data, { token }),
};
