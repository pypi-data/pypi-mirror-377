from sort_algorithms_pack import MergeSort 
class BinarySearch():
  def search(self,arr,target,sorted = False):
    if not sorted:
      ms=MergeSort()
      ms.mergeSort(arr,0,len(arr)-1)
    left =0
    right = len(arr)-1
    while(left<=right):
      mid = left+(right-left)//2
      if arr[mid]==target:
        return mid
      elif arr[mid]<target:
        left =mid+1
      else:
        right=mid-1
    return -1

def main():
  data1 = [1,2,3,4,5]
  data2=[3,2,5,4,1]
  bs = BinarySearch()
  print(bs.search(data1,3,True))
  print(bs.search(data2,3))

if __name__=="__main__":
  main()