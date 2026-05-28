/**
 * Skeleton loaders shown while the /analyze-ticket request is in flight.
 * Mirrors the shape of the eventual result cards so the layout doesn't shift.
 */

function Bar({ width = "w-full", height = "h-3" }) {
  return <div className={`${width} ${height} rounded bg-slate-200 animate-pulse`} />;
}

function CardSkeleton() {
  return (
    <div className="
      bg-white border border-slate-200/80 rounded-xl p-5
      shadow-[0_1px_2px_rgba(15,23,42,0.04),0_1px_3px_rgba(15,23,42,0.03)]
    ">
      <Bar width="w-24" height="h-3" />
      <div className="mt-4 flex flex-col gap-2">
        <Bar />
        <Bar width="w-5/6" />
        <Bar width="w-2/3" />
      </div>
    </div>
  );
}

export default function SkeletonResults() {
  return (
    <div className="flex flex-col gap-4 animate-fade-in">
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
    </div>
  );
}
