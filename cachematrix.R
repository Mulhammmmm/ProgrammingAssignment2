## Put comments here that give an overall description of what your
## functions do

## Write a short comment describing this function

makeCacheMatrix <- function(x = matrix()) {
  inv <- NULL
  
  set <- function(y) {
    x <<- y
    inv <<- NULL
  }
  
  get <- function() x
  
  setinverse <- function(inverse) inv <<- inverse
  
  getinverse <- function() inv
  
  list(set = set, 
       get = get,
       setinverse = setinverse,
       getinverse = getinverse)
}


## Write a short comment describing this function

cacheSolve <- function(x, ...) {
   inv <- x$getinverse()
  
  if (!is.null(inv)) {
    message("getting cached inverse")
    return(inv)
  }
  
  data <- x$get()
  inv <- solve(data, ...)
  x$setinverse(inv)
  inv       ## Return a matrix that is the inverse of 'x'
}
# Create a matrix
mat <- matrix(c(2, 1, 1, 2), 2, 2)

# Create the cache matrix object
cm <- makeCacheMatrix(mat)

# First time: computes and caches the inverse
cacheSolve(cm)

# Second time: retrieves from cache
cacheSolve(cm)
