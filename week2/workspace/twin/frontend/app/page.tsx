import Twin from '@/components/twin';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-cyan-50 via-sky-50 to-blue-50 relative overflow-hidden">
      {/* Subtle animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-cyan-200/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-sky-200/20 rounded-full blur-3xl animate-pulse delay-700" />
      </div>

      <div className="container mx-auto px-4 py-6 md:py-8 h-screen flex flex-col relative z-10">
        <div className="max-w-6xl mx-auto w-full flex flex-col h-full">
          {/* Elegant header */}
          <div className="text-center mb-4 md:mb-6">
            <div className="inline-block">
              <h1 className="text-4xl md:text-6xl font-extrabold bg-gradient-to-r from-cyan-600 via-sky-500 to-cyan-600 bg-clip-text text-transparent tracking-tight pb-2">
                Digital Twin
              </h1>
              <div className="h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent rounded-full mt-2" />
            </div>
            <p className="text-sm md:text-base text-cyan-600/80 mt-3 font-medium tracking-wide">
              Nagarjun Rajendran
            </p>
          </div>

          {/* Chat interface with elegant frame */}
          <div className="flex-1 min-h-0 mb-4">
            <Twin />
          </div>

          {/* Minimalist footer */}
          <footer className="text-center">
            <div className="inline-block bg-white/40 backdrop-blur-sm rounded-full px-6 py-2 border border-cyan-200/50">
              <p className="text-xs text-cyan-600/70">
                &copy; {new Date().getFullYear()} · AI-Powered Insights · 
                <span className="text-cyan-500/60 ml-1">Verify independently</span>
              </p>
            </div>
          </footer>
        </div>
      </div>
    </main>
  );
}