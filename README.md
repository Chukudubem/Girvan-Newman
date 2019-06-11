# Girvan-Newman
This is an implementation of Girvan Newman algorithm using Spark


DESCRIBING PARALLEL COMPUTATION OF EDGE BETWEENESS USING SPARK

To compute the betweeness code in parallel:
1. The first thing I did was generate an adjacency matrix that stores each nodes neighbor in a dictionary.
	
	{'a': ['b', 'e'],
             'b': ['a', 'g', 'f'],
             'd': ['g', 'f'],
             'e': ['a', 'f'],
             'f': ['b', 'd', 'e'],
             'g': ['b', 'd']}

2. Next, I find the distinct nodes and store them in a list.

3. I load the nodes gotten in step 2, using sc.parrallelize(**list of nodes**, 7)

4. The value 7 is the number of partitions for the nodes being loaded into an RDD. This way, for the sample input, each node is in its own partition and when we use data with larger nodes, it partitions the nodes as required. len(list of nodes)/7

5. The rest of the computation is done on each partition in parallel.
© 2019 GitHub, Inc.
