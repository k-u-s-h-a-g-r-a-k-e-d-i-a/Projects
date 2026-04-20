export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center">
      <h1 className="text-4xl font-bold mb-4 text-silver">NCRB Crime Analysis</h1>
      <p className="text-ash max-w-2xl mb-8">
        Interactive dashboard for visualizing and forecasting crime records from Delhi and Kerala.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
        <div className="p-6 bg-charcoal border border-storm rounded-lg shadow-card">
          <h2 className="text-xl font-semibold mb-2 text-intel">Delhi Records</h2>
          <p className="text-pewter text-sm">2001 – 2021 | 17 Categories</p>
        </div>
        
        <div className="p-6 bg-charcoal border border-storm rounded-lg shadow-card">
          <h2 className="text-xl font-semibold mb-2 text-safe">Kerala Records</h2>
          <p className="text-pewter text-sm">2016 – 2021 | 69 Categories</p>
        </div>
      </div>

      <div className="mt-12 p-4 bg-slate rounded-md border border-storm">
        <p className="text-pewter text-xs italic">
          Select a region from the sidebar (implementation pending) to begin your analysis.
        </p>
      </div>
    </div>
  );
}
