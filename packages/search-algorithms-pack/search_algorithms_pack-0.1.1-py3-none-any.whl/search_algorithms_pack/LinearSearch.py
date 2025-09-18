class LinearSearch():
  def search(self,arr,target):
    for i in range(len(arr)):
      if arr[i]==target:
        return i
    return -1
def main():
  ls =LinearSearch()
  print(ls.search([1,2,3,4,7,6],6))
if __name__=="__main__":
  main()