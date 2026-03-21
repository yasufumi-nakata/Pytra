# Generated std/math.rb delegates host bindings through this native seam.
# source: src/runtime/cs/std/math_native.cs (reference)

module MathNative
  def self.pi = Math::PI
  def self.e = Math::E
  def self.sqrt(x) = Math.sqrt(x.to_f)
  def self.sin(x) = Math.sin(x.to_f)
  def self.cos(x) = Math.cos(x.to_f)
  def self.tan(x) = Math.tan(x.to_f)
  def self.exp(x) = Math.exp(x.to_f)
  def self.log(x) = Math.log(x.to_f)
  def self.log10(x) = Math.log10(x.to_f)
  def self.fabs(x) = x.to_f.abs
  def self.floor(x) = x.to_f.floor.to_f
  def self.ceil(x) = x.to_f.ceil.to_f
  def self.pow(x, y) = x.to_f ** y.to_f
end
