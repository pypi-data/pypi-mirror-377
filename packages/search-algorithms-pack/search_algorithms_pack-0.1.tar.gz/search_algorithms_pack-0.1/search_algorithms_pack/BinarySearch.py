from sort_algorithms_pack import MergeSort 
class BinarySearch():
  def search(arr,target,sorted = False):
    if not sorted:
      arr = MergeSort.mergeSort(arr,0,len(arr)-1)
    left =0,right = len(arr)-1
    while(left<=right):
      mid = left+(right-left)//2
      if arr[mid]==target:
        return mid
      elif arr[mid]<target:
        left =mid+1
      else:
        right=mid-1
    return -1