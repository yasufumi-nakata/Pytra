# Generated std/time.rb delegates host bindings through this native seam.
# source: src/runtime/cs/std/time_native.cs (reference)

module TimeNative
  def self.perf_counter
    Process.clock_gettime(Process::CLOCK_MONOTONIC)
  end
end
