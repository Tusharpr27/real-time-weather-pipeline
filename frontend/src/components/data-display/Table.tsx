import React from 'react';

export interface TableColumn<T> {
  key: keyof T;
  header: string;
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  rowKey: keyof T;
  striped?: boolean;
  hoverable?: boolean;
  loading?: boolean;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onChange: (page: number) => void;
  };
}

export const Table = React.forwardRef<
  HTMLTableElement,
  TableProps<any>
>(
  (
    {
      data,
      columns,
      rowKey,
      striped = true,
      hoverable = true,
      loading = false,
      pagination,
    },
    ref
  ) => {
    return (
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table ref={ref} className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  style={{ width: col.width }}
                  className="px-4 py-3 text-left text-sm font-semibold text-gray-700"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="text-center py-8">
                  <span className="text-gray-500">Loading...</span>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="text-center py-8">
                  <span className="text-gray-500">No data available</span>
                </td>
              </tr>
            ) : (
              data.map((row, rowIndex) => (
                <tr
                  key={String(row[rowKey])}
                  className={`border-b border-gray-200 ${
                    striped && rowIndex % 2 === 0 ? 'bg-gray-50' : ''
                  } ${hoverable ? 'hover:bg-blue-50 transition-colors' : ''}`}
                >
                  {columns.map((col) => (
                    <td
                      key={String(col.key)}
                      className="px-4 py-3 text-sm text-gray-700"
                    >
                      {col.render
                        ? col.render(row[col.key], row)
                        : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>

        {pagination && (
          <div className="flex items-center justify-between p-4 bg-gray-50 border-t border-gray-200">
            <span className="text-sm text-gray-600">
              Page {pagination.page} of{' '}
              {Math.ceil(pagination.total / pagination.pageSize)}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => pagination.onChange(pagination.page - 1)}
                disabled={pagination.page === 1}
                className="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => pagination.onChange(pagination.page + 1)}
                disabled={
                  pagination.page >=
                  Math.ceil(pagination.total / pagination.pageSize)
                }
                className="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }
);

Table.displayName = 'Table';
