import React, { useEffect, useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
  SortingState,
} from '@tanstack/react-table';
import { Button } from './ui/button';
import { Loader2, ArrowUpDown, ChevronLeft, ChevronRight, Download, Search } from 'lucide-react';
import { cn } from '../lib/utils';

interface TableViewProps {
  fileName: string | null;
}

export default function TableView({ fileName }: TableViewProps) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('');

  useEffect(() => {
    if (!fileName) return;
    setLoading(true);
    fetch(`/api/data?file=${fileName}`)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [fileName]);

  const columns = useMemo(() => {
    if (data.length === 0) return [];
    const keys = Object.keys(data[0]);
    const helper = createColumnHelper<any>();

    return keys.map(key => 
      helper.accessor(key, {
        header: ({ column }) => {
          return (
            <Button
              variant="ghost"
              onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
              className="-ml-4 h-8 data-[state=open]:bg-accent"
            >
              <span className="capitalize">{key.replace(/_/g, ' ')}</span>
              <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
          )
        },
        cell: (info) => {
          const val = info.getValue();
          // Render links for URLs
          if (typeof val === 'string' && (val.startsWith('http') || val.startsWith('www'))) {
            return <a href={val} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline max-w-[200px] truncate block" title={val}>{val}</a>
          }
          return <div className="max-w-[300px] truncate" title={val}>{val}</div>
        }
      })
    );
  }, [data]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
  });

  if (loading) {
     return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!data.length) {
    return <div className="p-8 text-center text-slate-500">No data found in this file.</div>;
  }

  return (
    <div className="space-y-4 p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-slate-900">{fileName}</h2>
            <span className="text-sm text-slate-500">({data.length} rows)</span>
        </div>
        <div className="flex items-center gap-2">
            <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-500" />
                <input
                    placeholder="Search..."
                    value={globalFilter ?? ""}
                    onChange={(event) => setGlobalFilter(event.target.value)}
                    className="h-9 w-[250px] rounded-md border border-slate-200 bg-white px-3 py-1 pl-8 text-sm shadow-sm transition-colors placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-slate-950"
                />
            </div>
            <Button variant="outline" size="sm" onClick={() => {
                // Simple export functionality
                const csvContent = "data:text/csv;charset=utf-8," 
                    + [Object.keys(data[0]).join(","), ...data.map(row => Object.values(row).map(v => `"${v}"`).join(",") )].join("\n");
                const encodedUri = encodeURI(csvContent);
                const link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", fileName || "export.csv");
                document.body.appendChild(link);
                link.click();
            }}>
                <Download className="mr-2 h-4 w-4" />
                Export
            </Button>
        </div>
      </div>

      <div className="rounded-md border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="relative w-full overflow-auto" style={{ maxHeight: 'calc(100vh - 250px)' }}>
            <table className="w-full caption-bottom text-sm text-left">
            <thead className="[&_tr]:border-b sticky top-0 bg-slate-50 z-10">
                {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id} className="border-b transition-colors hover:bg-slate-100/50 data-[state=selected]:bg-slate-100">
                    {headerGroup.headers.map(header => (
                    <th key={header.id} className="h-10 px-4 text-left align-middle font-medium text-slate-500 [&:has([role=checkbox])]:pr-0">
                        {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                            )}
                    </th>
                    ))}
                </tr>
                ))}
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
                {table.getRowModel().rows.length ? (
                table.getRowModel().rows.map(row => (
                    <tr
                    key={row.id}
                    className="border-b transition-colors hover:bg-slate-100/50 data-[state=selected]:bg-slate-100"
                    >
                    {row.getVisibleCells().map(cell => (
                        <td key={cell.id} className="p-2 px-4 align-middle [&:has([role=checkbox])]:pr-0 text-slate-700">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                    ))}
                    </tr>
                ))
                ) : (
                <tr>
                    <td colSpan={columns.length} className="h-24 text-center">
                    No results.
                    </td>
                </tr>
                )
                }
            </tbody>
            </table>
        </div>
      </div>

      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-slate-500">
            Page {table.getState().pagination.pageIndex + 1} of{" "}
            {table.getPageCount()}
        </div>
        <div className="space-x-2">
            <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            >
            <ChevronLeft className="h-4 w-4" />
            Previous
            </Button>
            <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            >
            Next
            <ChevronRight className="h-4 w-4" />
            </Button>
        </div>
      </div>
    </div>
  );
}