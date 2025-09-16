class MergeSort:
  def __Merge(self,arr,low:int,mid:int,high:int):
    leftSize = mid-low+1
    rightSize = high -mid
    left=[]
    right=[]
    for f in range(low,mid+1):
      left.append(arr[f])
    for s in range(mid+1,high+1):
      right.append(arr[s])
    i=j=0
    k=low
    while i<leftSize and j<rightSize:
      if left[i]<right[j]:
        arr[k]=left[i]
        k=k+1
        i+=1
      else:
        arr[k]=right[j]
        k+=1
        j+=1
    while i<leftSize:
      arr[k]=left[i]
      k+=1
      i+=1
    while j<rightSize:
      arr[k]=right[j]
      k+=1
      j+=1
  def mergeSort(self,arr,low,high):
    if low<high:
      mid = low+(high-low)//2
      self.mergeSort(arr,low,mid)
      self.mergeSort(arr,mid+1,high)
      self.__Merge(arr,low,mid,high)
class QuickSort():
  @staticmethod
  def __swap(arr,i:int,j:int):
    arr[i],arr[j]=arr[j],arr[i]
  def __partition(self,arr,low,high):
    pivot = arr[high]
    j=low-1
    for i in range(low,high):
      if(arr[i]<pivot):
        j+=1
        self.__swap(arr,i,j)
        
    QuickSort.__swap(arr,j+1,high)
    return j+1
  def quickSort(self,arr,low,high):
    if low<high:
      pivot = self.__partition(arr,low,high)
      self.quickSort(arr,low,pivot-1)
      self.quickSort(arr,pivot+1,high)
def main():
  sort = MergeSort()
  size = int(input("Enter the size of array: "))
  arr=[]
  for i in range(size):
    arr.append(int(input(f"Enter the {i+1}th term: ")))
  sort.mergeSort(arr,0,size-1)
  

if __name__ == "__main__":
  main()