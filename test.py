import subprocess as sb

p = sb.Popen(["make", "-C", "tools"])
p.wait()
print(p.returncode)