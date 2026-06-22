import TransactionsTable from "@/components/tables/TransactionsTable";
import { useTransactions } from "@/hooks/useFraudData";

export default function Transactions() {
  const { data, isLoading, isError, error } = useTransactions();
  return (
    <TransactionsTable
      rows={data || []}
      loading={isLoading}
      error={isError ? error : null}
    />
  );
}
