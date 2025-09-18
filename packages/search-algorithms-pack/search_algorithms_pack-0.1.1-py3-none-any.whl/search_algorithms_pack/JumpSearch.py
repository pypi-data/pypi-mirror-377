from sort_algorithms_pack import MergeSort
class JumpSearch():
  def search(self,arr,target,sorted =False):
    if not sorted:
      ms = MergeSort()
      ms.mergeSort(arr,0,len(arr)-1)
    n = len(arr)
    jump=prev=0
    while jump<n:
      if arr[jump]==target:
        return jump
      if arr[jump]<target:
        prev =jump
        jump = jump+ int(pow(n,0.5))
      else:
        break
    if jump == n-1:
      return -1
    for j in range(prev,jump):
      if arr[j]==target:
        return j
    return -1

def main():
  s = JumpSearch()
  print(s.search([2,3,7,9,10,11,23,24],14,True))

if __name__ =="__main__":
  main()