# Basic Example

This is a basic example of how to use the `py-lerchs-grossmann` package to obtain the optimum pit in a block model.

## Block Model

The block model must have the following columns: `id` and `value`, for the proper performance of the package. Other columns or extra data do not affect the performance of the package. In this example, the columns `x`, `y`, and `z` are not used by the algorithm.

### Example

![](../img/basic_example_block_model.png)

| id  | x   | y   | z   | value |
| --- | --- | --- | --- | ----- |
| 1   | 1   | 1   | 3   | -1    |
| 2   | 2   | 1   | 3   | -1    |
| 3   | 3   | 1   | 3   | -1    |
| 4   | 4   | 1   | 3   | -1    |
| 5   | 5   | 1   | 3   | -1    |
| 6   | 2   | 1   | 2   | -1    |
| 7   | 3   | 1   | 2   | -1    |
| 8   | 4   | 1   | 2   | 3     |
| 9   | 3   | 1   | 1   | 5     |

## Arc DataFrame

The Arc DataFrame is a table that contains the connections or arcs between the blocks. This is because, to mine a block, you must first mine the blocks above it.

![basic_example_arcs](../img/basic_example_arcs.png)

Following the image, the Arc DataFrame should look like:

| start | end |
| ----- | --- |
| 6     | 1   |
| 6     | 2   |
| 6     | 3   |
| 7     | 2   |
| 7     | 3   |
| 7     | 4   |
| 8     | 3   |
| 8     | 4   |
| 8     | 5   |
| 9     | 6   |
| 9     | 7   |

## The `main` funtion

Using the block model with the `id` and `value` columns, and the arc DataFrame, the `main` function executes the Lerchs-Grossmann algorithm.

```python
import pandas as pd
import py_lerchs_grossmann as plg

# Define block and arc data
df_y = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "x": [1, 2, 3, 4, 5, 2, 3, 4, 3],
        "y": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "z": [3, 3, 3, 3, 3, 2, 2, 2, 1],
        "value": [-1, -1, -1, -1, -1, -1, -1, 3, 5],
    }
)

df_arc = pd.DataFrame(
    {
        "start": [6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9],
        "end": [1, 2, 3, 2, 3, 4, 3, 4, 5, 6, 7, 8],
    }
)

df_pit = main(df_y, df_arc, True)
```

If the argument `verbose=True`, the function will print each step of the algorithm in the terminal.

```Terminal
builded df_y_copy time:0.0 seconds
builded df_x time:0.0010006427764892578 seconds
builded df_arc_positive time:0.0022470951080322266 seconds
builded mask time:0.0022470951080322266 seconds
filtered df_y_copy time:0.0022470951080322266 seconds
Start for len:9

---------------
Counter cicle 1 -> time cicle 0.0 seconds
---------------
possible_arc
   start  end
0      8    3
1      8    4
2      8    5
3      9    6
4      9    7
df_arc_positive
   start_real  end_real  value  type  strength
0           0         1     -1   NaN       NaN
1           0         2     -1   NaN       NaN
2           0         3     -1   NaN       NaN
3           0         4     -1   NaN       NaN
4           0         5     -1   NaN       NaN
5           0         6     -1   NaN       NaN
6           0         7     -1   NaN       NaN
7           0         8      3   NaN       NaN
8           0         9      5   NaN       NaN

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        8
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         3    NaN  NaN      NaN
3           0         4    NaN  NaN      NaN
4           0         5    NaN  NaN      NaN
5           0         6    NaN  NaN      NaN
6           0         7    NaN  NaN      NaN
7           0         9    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         3    NaN  NaN      NaN
3           0         4    NaN  NaN      NaN
4           0         5    NaN  NaN      NaN
5           0         6    NaN  NaN      NaN
6           0         7    NaN  NaN      NaN
7           0         9    NaN  NaN      NaN
8           8         3    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0    NaN
1         0.0       2.0    NaN
2         0.0       3.0    NaN
3         0.0       4.0    NaN
4         0.0       5.0    NaN
5         0.0       6.0    NaN
6         0.0       7.0    NaN
7         0.0       9.0    NaN
8         3.0       8.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       3.0    NaN
3         0.0       4.0   -1.0
4         0.0       5.0   -1.0
5         0.0       6.0   -1.0
6         0.0       7.0   -1.0
7         0.0       9.0    5.0
8         3.0       8.0    3.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       3.0    2.0
3         0.0       4.0   -1.0
4         0.0       5.0   -1.0
5         0.0       6.0   -1.0
6         0.0       7.0   -1.0
7         0.0       9.0    5.0
8         3.0       8.0    3.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0  NaN      NaN
1           0         2   -1.0  NaN      NaN
2           0         3    2.0  NaN      NaN
3           0         4   -1.0  NaN      NaN
4           0         5   -1.0  NaN      NaN
5           0         6   -1.0  NaN      NaN
6           0         7   -1.0  NaN      NaN
7           0         9    5.0  NaN      NaN
8           8         3    3.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         3    2.0    p   strong
3           0         4   -1.0    p     weak
4           0         5   -1.0    p     weak
5           0         6   -1.0    p     weak
6           0         7   -1.0    p     weak
7           0         9    5.0    p   strong
8           8         3    3.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   3  3.0  1.0  3.0     -1
2   8  4.0  1.0  2.0      3
3   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
0   1  1  1  3     -1
1   2  2  1  3     -1
3   4  4  1  3     -1
4   5  5  1  3     -1
5   6  2  1  2     -1
6   7  3  1  2     -1

---------------
Counter cicle 2 -> time cicle 0.06424283981323242 seconds
---------------
possible_arc
   start  end
0      8    4
1      8    5
2      9    6
3      9    7
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         3    2.0    p   strong
3           0         4   -1.0    p     weak
4           0         5   -1.0    p     weak
5           0         6   -1.0    p     weak
6           0         7   -1.0    p     weak
7           0         9    5.0    p   strong
8           8         3    3.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        3
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         4    NaN  NaN      NaN
3           0         5    NaN  NaN      NaN
4           0         6    NaN  NaN      NaN
5           0         7    NaN  NaN      NaN
6           0         9    NaN  NaN      NaN
7           8         3    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         4    NaN  NaN      NaN
3           0         5    NaN  NaN      NaN
4           0         6    NaN  NaN      NaN
5           0         7    NaN  NaN      NaN
6           0         9    NaN  NaN      NaN
7           8         3    NaN  NaN      NaN
8           8         4    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0    NaN
1         0.0       2.0    NaN
2         0.0       4.0    NaN
3         0.0       5.0    NaN
4         0.0       6.0    NaN
5         0.0       7.0    NaN
6         0.0       9.0    NaN
7         4.0       8.0    NaN
8         8.0       3.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       4.0    NaN
3         0.0       5.0   -1.0
4         0.0       6.0   -1.0
5         0.0       7.0   -1.0
6         0.0       9.0    5.0
7         4.0       8.0    NaN
8         8.0       3.0   -1.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       4.0    1.0
3         0.0       5.0   -1.0
4         0.0       6.0   -1.0
5         0.0       7.0   -1.0
6         0.0       9.0    5.0
7         4.0       8.0    2.0
8         8.0       3.0   -1.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0  NaN      NaN
1           0         2   -1.0  NaN      NaN
2           0         4    1.0  NaN      NaN
3           0         5   -1.0  NaN      NaN
4           0         6   -1.0  NaN      NaN
5           0         7   -1.0  NaN      NaN
6           0         9    5.0  NaN      NaN
7           8         3   -1.0  NaN      NaN
8           8         4    2.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         4    1.0    p   strong
3           0         5   -1.0    p     weak
4           0         6   -1.0    p     weak
5           0         7   -1.0    p     weak
6           0         9    5.0    p   strong
7           8         3   -1.0    p     weak
8           8         4    2.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   3  3.0  1.0  3.0     -1
2   4  4.0  1.0  3.0     -1
3   8  4.0  1.0  2.0      3
4   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
0   1  1  1  3     -1
1   2  2  1  3     -1
4   5  5  1  3     -1
5   6  2  1  2     -1
6   7  3  1  2     -1

---------------
Counter cicle 3 -> time cicle 0.07159423828125 seconds
---------------
possible_arc
   start  end
0      8    5
1      9    6
2      9    7
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         4    1.0    p   strong
3           0         5   -1.0    p     weak
4           0         6   -1.0    p     weak
5           0         7   -1.0    p     weak
6           0         9    5.0    p   strong
7           8         3   -1.0    p     weak
8           8         4    2.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        4
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         5    NaN  NaN      NaN
3           0         6    NaN  NaN      NaN
4           0         7    NaN  NaN      NaN
5           0         9    NaN  NaN      NaN
6           8         3    NaN  NaN      NaN
7           8         4    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         5    NaN  NaN      NaN
3           0         6    NaN  NaN      NaN
4           0         7    NaN  NaN      NaN
5           0         9    NaN  NaN      NaN
6           8         3    NaN  NaN      NaN
7           8         4    NaN  NaN      NaN
8           8         5    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0    NaN
1         0.0       2.0    NaN
2         0.0       5.0    NaN
3         0.0       6.0    NaN
4         0.0       7.0    NaN
5         0.0       9.0    NaN
6         5.0       8.0    NaN
7         8.0       3.0    NaN
8         8.0       4.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       5.0    NaN
3         0.0       6.0   -1.0
4         0.0       7.0   -1.0
5         0.0       9.0    5.0
6         5.0       8.0    NaN
7         8.0       3.0   -1.0
8         8.0       4.0   -1.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       5.0    0.0
3         0.0       6.0   -1.0
4         0.0       7.0   -1.0
5         0.0       9.0    5.0
6         5.0       8.0    1.0
7         8.0       3.0   -1.0
8         8.0       4.0   -1.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0  NaN      NaN
1           0         2   -1.0  NaN      NaN
2           0         5    0.0  NaN      NaN
3           0         6   -1.0  NaN      NaN
4           0         7   -1.0  NaN      NaN
5           0         9    5.0  NaN      NaN
6           8         3   -1.0  NaN      NaN
7           8         4   -1.0  NaN      NaN
8           8         5    1.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         5    0.0    p     weak
3           0         6   -1.0    p     weak
4           0         7   -1.0    p     weak
5           0         9    5.0    p   strong
6           8         3   -1.0    p     weak
7           8         4   -1.0    p     weak
8           8         5    1.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
0   1  1  1  3     -1
1   2  2  1  3     -1
2   3  3  1  3     -1
3   4  4  1  3     -1
4   5  5  1  3     -1
5   6  2  1  2     -1
6   7  3  1  2     -1
7   8  4  1  2      3

---------------
Counter cicle 4 -> time cicle 0.07389569282531738 seconds
---------------
possible_arc
   start  end
0      9    6
1      9    7
2      9    8
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         5    0.0    p     weak
3           0         6   -1.0    p     weak
4           0         7   -1.0    p     weak
5           0         9    5.0    p   strong
6           8         3   -1.0    p     weak
7           8         4   -1.0    p     weak
8           8         5    1.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        9
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         5    NaN  NaN      NaN
3           0         6    NaN  NaN      NaN
4           0         7    NaN  NaN      NaN
5           8         3    NaN  NaN      NaN
6           8         4    NaN  NaN      NaN
7           8         5    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         5    NaN  NaN      NaN
3           0         6    NaN  NaN      NaN
4           0         7    NaN  NaN      NaN
5           8         3    NaN  NaN      NaN
6           8         4    NaN  NaN      NaN
7           8         5    NaN  NaN      NaN
8           9         6    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0    NaN
1         0.0       2.0    NaN
2         0.0       5.0    NaN
3         0.0       6.0    NaN
4         0.0       7.0    NaN
5         5.0       8.0    NaN
6         6.0       9.0    NaN
7         8.0       3.0    NaN
8         8.0       4.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       5.0    NaN
3         0.0       6.0    NaN
4         0.0       7.0   -1.0
5         5.0       8.0    NaN
6         6.0       9.0    5.0
7         8.0       3.0   -1.0
8         8.0       4.0   -1.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0   -1.0
1         0.0       2.0   -1.0
2         0.0       5.0    0.0
3         0.0       6.0    4.0
4         0.0       7.0   -1.0
5         5.0       8.0    1.0
6         6.0       9.0    5.0
7         8.0       3.0   -1.0
8         8.0       4.0   -1.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0  NaN      NaN
1           0         2   -1.0  NaN      NaN
2           0         5    0.0  NaN      NaN
3           0         6    4.0  NaN      NaN
4           0         7   -1.0  NaN      NaN
5           8         3   -1.0  NaN      NaN
6           8         4   -1.0  NaN      NaN
7           8         5    1.0  NaN      NaN
8           9         6    5.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         5    0.0    p     weak
3           0         6    4.0    p   strong
4           0         7   -1.0    p     weak
5           8         3   -1.0    p     weak
6           8         4   -1.0    p     weak
7           8         5    1.0    m     weak
8           9         6    5.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   6  2.0  1.0  2.0     -1
2   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
0   1  1  1  3     -1
1   2  2  1  3     -1
2   3  3  1  3     -1
3   4  4  1  3     -1
4   5  5  1  3     -1
6   7  3  1  2     -1
7   8  4  1  2      3

---------------
Counter cicle 5 -> time cicle 0.06777811050415039 seconds
---------------
possible_arc
   start  end
0      6    1
1      6    2
2      6    3
3      9    7
4      9    8
df_arc_positive
   start_real  end_real  value type strength
0           0         1   -1.0    p     weak
1           0         2   -1.0    p     weak
2           0         5    0.0    p     weak
3           0         6    4.0    p   strong
4           0         7   -1.0    p     weak
5           8         3   -1.0    p     weak
6           8         4   -1.0    p     weak
7           8         5    1.0    m     weak
8           9         6    5.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        6
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         5    NaN  NaN      NaN
3           0         7    NaN  NaN      NaN
4           8         3    NaN  NaN      NaN
5           8         4    NaN  NaN      NaN
6           8         5    NaN  NaN      NaN
7           9         6    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         1    NaN  NaN      NaN
1           0         2    NaN  NaN      NaN
2           0         5    NaN  NaN      NaN
3           0         7    NaN  NaN      NaN
4           8         3    NaN  NaN      NaN
5           8         4    NaN  NaN      NaN
6           8         5    NaN  NaN      NaN
7           9         6    NaN  NaN      NaN
8           6         1    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0    NaN
1         0.0       2.0    NaN
2         0.0       5.0    NaN
3         0.0       7.0    NaN
4         5.0       8.0    NaN
5         1.0       6.0    NaN
6         8.0       3.0    NaN
7         8.0       4.0    NaN
8         6.0       9.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0    NaN
1         0.0       2.0   -1.0
2         0.0       5.0    NaN
3         0.0       7.0   -1.0
4         5.0       8.0    NaN
5         1.0       6.0    NaN
6         8.0       3.0   -1.0
7         8.0       4.0   -1.0
8         6.0       9.0    5.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       1.0    3.0
1         0.0       2.0   -1.0
2         0.0       5.0    0.0
3         0.0       7.0   -1.0
4         5.0       8.0    1.0
5         1.0       6.0    4.0
6         8.0       3.0   -1.0
7         8.0       4.0   -1.0
8         6.0       9.0    5.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         1    3.0  NaN      NaN
1           0         2   -1.0  NaN      NaN
2           0         5    0.0  NaN      NaN
3           0         7   -1.0  NaN      NaN
4           8         3   -1.0  NaN      NaN
5           8         4   -1.0  NaN      NaN
6           8         5    1.0  NaN      NaN
7           9         6    5.0  NaN      NaN
8           6         1    4.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         1    3.0    p   strong
1           0         2   -1.0    p     weak
2           0         5    0.0    p     weak
3           0         7   -1.0    p     weak
4           8         3   -1.0    p     weak
5           8         4   -1.0    p     weak
6           8         5    1.0    m     weak
7           9         6    5.0    m     weak
8           6         1    4.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   1  1.0  1.0  3.0     -1
2   6  2.0  1.0  2.0     -1
3   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
1   2  2  1  3     -1
2   3  3  1  3     -1
3   4  4  1  3     -1
4   5  5  1  3     -1
6   7  3  1  2     -1
7   8  4  1  2      3

---------------
Counter cicle 6 -> time cicle 0.06540465354919434 seconds
---------------
possible_arc
   start  end
0      6    2
1      6    3
2      9    7
3      9    8
df_arc_positive
   start_real  end_real  value type strength
0           0         1    3.0    p   strong
1           0         2   -1.0    p     weak
2           0         5    0.0    p     weak
3           0         7   -1.0    p     weak
4           8         3   -1.0    p     weak
5           8         4   -1.0    p     weak
6           8         5    1.0    m     weak
7           9         6    5.0    m     weak
8           6         1    4.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        1
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         2    NaN  NaN      NaN
1           0         5    NaN  NaN      NaN
2           0         7    NaN  NaN      NaN
3           8         3    NaN  NaN      NaN
4           8         4    NaN  NaN      NaN
5           8         5    NaN  NaN      NaN
6           9         6    NaN  NaN      NaN
7           6         1    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         2    NaN  NaN      NaN
1           0         5    NaN  NaN      NaN
2           0         7    NaN  NaN      NaN
3           8         3    NaN  NaN      NaN
4           8         4    NaN  NaN      NaN
5           8         5    NaN  NaN      NaN
6           9         6    NaN  NaN      NaN
7           6         1    NaN  NaN      NaN
8           6         2    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       2.0    NaN
1         0.0       5.0    NaN
2         0.0       7.0    NaN
3         5.0       8.0    NaN
4         2.0       6.0    NaN
5         8.0       3.0    NaN
6         8.0       4.0    NaN
7         6.0       1.0    NaN
8         6.0       9.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       2.0    NaN
1         0.0       5.0    NaN
2         0.0       7.0   -1.0
3         5.0       8.0    NaN
4         2.0       6.0    NaN
5         8.0       3.0   -1.0
6         8.0       4.0   -1.0
7         6.0       1.0   -1.0
8         6.0       9.0    5.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       2.0    2.0
1         0.0       5.0    0.0
2         0.0       7.0   -1.0
3         5.0       8.0    1.0
4         2.0       6.0    3.0
5         8.0       3.0   -1.0
6         8.0       4.0   -1.0
7         6.0       1.0   -1.0
8         6.0       9.0    5.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         2    2.0  NaN      NaN
1           0         5    0.0  NaN      NaN
2           0         7   -1.0  NaN      NaN
3           8         3   -1.0  NaN      NaN
4           8         4   -1.0  NaN      NaN
5           8         5    1.0  NaN      NaN
6           9         6    5.0  NaN      NaN
7           6         1   -1.0  NaN      NaN
8           6         2    3.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         2    2.0    p   strong
1           0         5    0.0    p     weak
2           0         7   -1.0    p     weak
3           8         3   -1.0    p     weak
4           8         4   -1.0    p     weak
5           8         5    1.0    m     weak
6           9         6    5.0    m     weak
7           6         1   -1.0    p     weak
8           6         2    3.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   1  1.0  1.0  3.0     -1
2   2  2.0  1.0  3.0     -1
3   6  2.0  1.0  2.0     -1
4   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
2   3  3  1  3     -1
3   4  4  1  3     -1
4   5  5  1  3     -1
6   7  3  1  2     -1
7   8  4  1  2      3

---------------
Counter cicle 7 -> time cicle 0.07021951675415039 seconds
---------------
possible_arc
   start  end
0      6    3
1      9    7
2      9    8
df_arc_positive
   start_real  end_real  value type strength
0           0         2    2.0    p   strong
1           0         5    0.0    p     weak
2           0         7   -1.0    p     weak
3           8         3   -1.0    p     weak
4           8         4   -1.0    p     weak
5           8         5    1.0    m     weak
6           9         6    5.0    m     weak
7           6         1   -1.0    p     weak
8           6         2    3.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        2
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         5    NaN  NaN      NaN
1           0         7    NaN  NaN      NaN
2           8         3    NaN  NaN      NaN
3           8         4    NaN  NaN      NaN
4           8         5    NaN  NaN      NaN
5           9         6    NaN  NaN      NaN
6           6         1    NaN  NaN      NaN
7           6         2    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         5    NaN  NaN      NaN
1           0         7    NaN  NaN      NaN
2           8         3    NaN  NaN      NaN
3           8         4    NaN  NaN      NaN
4           8         5    NaN  NaN      NaN
5           9         6    NaN  NaN      NaN
6           6         1    NaN  NaN      NaN
7           6         2    NaN  NaN      NaN
8           6         3    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       5.0    NaN
1         0.0       7.0    NaN
2         5.0       8.0    NaN
3         8.0       3.0    NaN
4         8.0       4.0    NaN
5         3.0       6.0    NaN
6         6.0       1.0    NaN
7         6.0       2.0    NaN
8         6.0       9.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       5.0    NaN
1         0.0       7.0   -1.0
2         5.0       8.0    NaN
3         8.0       3.0    NaN
4         8.0       4.0   -1.0
5         3.0       6.0    NaN
6         6.0       1.0   -1.0
7         6.0       2.0   -1.0
8         6.0       9.0    5.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       5.0    2.0
1         0.0       7.0   -1.0
2         5.0       8.0    3.0
3         8.0       3.0    1.0
4         8.0       4.0   -1.0
5         3.0       6.0    2.0
6         6.0       1.0   -1.0
7         6.0       2.0   -1.0
8         6.0       9.0    5.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         5    2.0  NaN      NaN
1           0         7   -1.0  NaN      NaN
2           8         3    1.0  NaN      NaN
3           8         4   -1.0  NaN      NaN
4           8         5    3.0  NaN      NaN
5           9         6    5.0  NaN      NaN
6           6         1   -1.0  NaN      NaN
7           6         2   -1.0  NaN      NaN
8           6         3    2.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         5    2.0    p   strong
1           0         7   -1.0    p     weak
2           8         3    1.0    p   strong
3           8         4   -1.0    p     weak
4           8         5    3.0    m     weak
5           9         6    5.0    m     weak
6           6         1   -1.0    p     weak
7           6         2   -1.0    p     weak
8           6         3    2.0    m     weak

If there is a `strong` arc and `start_real` is not 0, a new arc is added with `start_real` set to 0 and the same end_real. The original arc is removed.
df_arc_positive
   start_real  end_real  value type strength
0           0         5    1.0    p   strong
1           0         7   -1.0    p     weak
2           0         3    1.0    p   strong
3           8         4   -1.0    p     weak
4           8         5    2.0    m     weak
5           9         6    5.0    m     weak
6           6         1   -1.0    p     weak
7           6         2   -1.0    p     weak
8           6         3    2.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   1  1.0  1.0  3.0     -1
2   2  2.0  1.0  3.0     -1
3   6  2.0  1.0  2.0     -1
4   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
2   3  3  1  3     -1
3   4  4  1  3     -1
4   5  5  1  3     -1
6   7  3  1  2     -1
7   8  4  1  2      3
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   1  1.0  1.0  3.0     -1
2   2  2.0  1.0  3.0     -1
3   3  3.0  1.0  3.0     -1
4   4  4.0  1.0  3.0     -1
5   5  5.0  1.0  3.0     -1
6   6  2.0  1.0  2.0     -1
7   8  4.0  1.0  2.0      3
8   9  3.0  1.0  1.0      5
df_y_copy
   id  x  y  z  value
6   7  3  1  2     -1

---------------
Counter cicle 8 -> time cicle 0.10406661033630371 seconds
---------------
possible_arc
   start  end
0      9    7
df_arc_positive
   start_real  end_real  value type strength
0           0         5    1.0    p   strong
1           0         7   -1.0    p     weak
2           0         3    1.0    p   strong
3           8         4   -1.0    p     weak
4           8         5    2.0    m     weak
5           9         6    5.0    m     weak
6           6         1   -1.0    p     weak
7           6         2   -1.0    p     weak
8           6         3    2.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        3
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         5    NaN  NaN      NaN
1           0         7    NaN  NaN      NaN
2           8         4    NaN  NaN      NaN
3           8         5    NaN  NaN      NaN
4           9         6    NaN  NaN      NaN
5           6         1    NaN  NaN      NaN
6           6         2    NaN  NaN      NaN
7           6         3    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         5    NaN  NaN      NaN
1           0         7    NaN  NaN      NaN
2           8         4    NaN  NaN      NaN
3           8         5    NaN  NaN      NaN
4           9         6    NaN  NaN      NaN
5           6         1    NaN  NaN      NaN
6           6         2    NaN  NaN      NaN
7           6         3    NaN  NaN      NaN
8           9         7    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       5.0    NaN
1         0.0       7.0    NaN
2         5.0       8.0    NaN
3         7.0       9.0    NaN
4         8.0       4.0    NaN
5         9.0       6.0    NaN
6         6.0       1.0    NaN
7         6.0       2.0    NaN
8         6.0       3.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       5.0    NaN
1         0.0       7.0    NaN
2         5.0       8.0    NaN
3         7.0       9.0    NaN
4         8.0       4.0   -1.0
5         9.0       6.0    NaN
6         6.0       1.0   -1.0
7         6.0       2.0   -1.0
8         6.0       3.0   -1.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       5.0    1.0
1         0.0       7.0    0.0
2         5.0       8.0    2.0
3         7.0       9.0    1.0
4         8.0       4.0   -1.0
5         9.0       6.0   -4.0
6         6.0       1.0   -1.0
7         6.0       2.0   -1.0
8         6.0       3.0   -1.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         5    1.0  NaN      NaN
1           0         7    0.0  NaN      NaN
2           8         4   -1.0  NaN      NaN
3           8         5    2.0  NaN      NaN
4           9         6   -4.0  NaN      NaN
5           6         1   -1.0  NaN      NaN
6           6         2   -1.0  NaN      NaN
7           6         3   -1.0  NaN      NaN
8           9         7    1.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         5    1.0    p   strong
1           0         7    0.0    p     weak
2           8         4   -1.0    p     weak
3           8         5    2.0    m     weak
4           9         6   -4.0    p     weak
5           6         1   -1.0    p     weak
6           6         2   -1.0    p     weak
7           6         3   -1.0    p     weak
8           9         7    1.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   4  4.0  1.0  3.0     -1
2   5  5.0  1.0  3.0     -1
3   8  4.0  1.0  2.0      3
df_y_copy
   id  x  y  z  value
0   1  1  1  3     -1
1   2  2  1  3     -1
2   3  3  1  3     -1
5   6  2  1  2     -1
6   7  3  1  2     -1
8   9  3  1  1      5

---------------
Counter cicle 9 -> time cicle 0.07696938514709473 seconds
---------------
possible_arc
   start  end
0      8    3
df_arc_positive
   start_real  end_real  value type strength
0           0         5    1.0    p   strong
1           0         7    0.0    p     weak
2           8         4   -1.0    p     weak
3           8         5    2.0    m     weak
4           9         6   -4.0    p     weak
5           6         1   -1.0    p     weak
6           6         2   -1.0    p     weak
7           6         3   -1.0    p     weak
8           9         7    1.0    m     weak

Find the root, the arc from X₀ to Xₘ
Root
start_real      0
end_real        5
value         NaN
type          NaN
strength      NaN
Name: 0, dtype: object
df_arc_positive
   start_real  end_real  value type strength
0           0         7    NaN  NaN      NaN
1           8         4    NaN  NaN      NaN
2           8         5    NaN  NaN      NaN
3           9         6    NaN  NaN      NaN
4           6         1    NaN  NaN      NaN
5           6         2    NaN  NaN      NaN
6           6         3    NaN  NaN      NaN
7           9         7    NaN  NaN      NaN

Add the arc from Xₖ to Xₗ
df_arc_positive
   start_real  end_real  value type strength
0           0         7    NaN  NaN      NaN
1           8         4    NaN  NaN      NaN
2           8         5    NaN  NaN      NaN
3           9         6    NaN  NaN      NaN
4           6         1    NaN  NaN      NaN
5           6         2    NaN  NaN      NaN
6           6         3    NaN  NaN      NaN
7           9         7    NaN  NaN      NaN
8           8         3    NaN  NaN      NaN

Create `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       7.0    NaN
1         7.0       9.0    NaN
2         9.0       6.0    NaN
3         6.0       1.0    NaN
4         6.0       2.0    NaN
5         6.0       3.0    NaN
6         3.0       8.0    NaN
7         8.0       4.0    NaN
8         8.0       5.0    NaN

Add `value` of the outermost nodes in `df_arc_direct_tree`
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       7.0    NaN
1         7.0       9.0    NaN
2         9.0       6.0    NaN
3         6.0       1.0   -1.0
4         6.0       2.0   -1.0
5         6.0       3.0    NaN
6         3.0       8.0    NaN
7         8.0       4.0   -1.0
8         8.0       5.0   -1.0

Compute the values of the arcs at the middle and root of the tree based on the sum of the outermost arcs and the node values.
df_arc_direct_tree
   start_tree  end_tree  value
0         0.0       7.0    1.0
1         7.0       9.0    2.0
2         9.0       6.0   -3.0
3         6.0       1.0   -1.0
4         6.0       2.0   -1.0
5         6.0       3.0    0.0
6         3.0       8.0    1.0
7         8.0       4.0   -1.0
8         8.0       5.0   -1.0

Add `values` from `df_arc_direct_tree` to `df_arc_positive`
df_arc_positive
   start_real  end_real  value type strength
0           0         7    1.0  NaN      NaN
1           8         4   -1.0  NaN      NaN
2           8         5   -1.0  NaN      NaN
3           9         6   -3.0  NaN      NaN
4           6         1   -1.0  NaN      NaN
5           6         2   -1.0  NaN      NaN
6           6         3    0.0  NaN      NaN
7           9         7    2.0  NaN      NaN
8           8         3    1.0  NaN      NaN

Compare `df_positive` and `df_arc_direct_tree` to classify the arcs in type (`p` or `m`) and the strength in (`strong` or `weak`)
df_arc_positive
   start_real  end_real  value type strength
0           0         7    1.0    p   strong
1           8         4   -1.0    p     weak
2           8         5   -1.0    p     weak
3           9         6   -3.0    p     weak
4           6         1   -1.0    p     weak
5           6         2   -1.0    p     weak
6           6         3    0.0    p     weak
7           9         7    2.0    m     weak
8           8         3    1.0    m     weak
df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   1  1.0  1.0  3.0     -1
2   2  2.0  1.0  3.0     -1
3   3  3.0  1.0  3.0     -1
4   4  4.0  1.0  3.0     -1
5   5  5.0  1.0  3.0     -1
6   6  2.0  1.0  2.0     -1
7   7  3.0  1.0  2.0     -1
8   8  4.0  1.0  2.0      3
9   9  3.0  1.0  1.0      5
df_y_copy
Empty DataFrame
Columns: [id, x, y, z, value]
Index: []

Algoritm completed !!!
------------------------
df_arc_positive
   start_real  end_real  value type strength
0           0         7    1.0    p   strong
1           8         4   -1.0    p     weak
2           8         5   -1.0    p     weak
3           9         6   -3.0    p     weak
4           6         1   -1.0    p     weak
5           6         2   -1.0    p     weak
6           6         3    0.0    p     weak
7           9         7    2.0    m     weak
8           8         3    1.0    m     weak

df_x
   id    x    y    z  value
0   0  NaN  NaN  NaN      0
1   1  1.0  1.0  3.0     -1
2   2  2.0  1.0  3.0     -1
3   3  3.0  1.0  3.0     -1
4   4  4.0  1.0  3.0     -1
5   5  5.0  1.0  3.0     -1
6   6  2.0  1.0  2.0     -1
7   7  3.0  1.0  2.0     -1
8   8  4.0  1.0  2.0      3
9   9  3.0  1.0  1.0      5

df_y_copy
Empty DataFrame
Columns: [id, x, y, z, value]
Index: []
Tiempo de ejecución: 0.7430 segundos
```

If you assign the result of the main function to a variable like `df_pit = main(df_y, df_arc, True)`, you can export it to a `.csv` file using the pandas package.

```python
df_pit = main(df_y, df_arc, True)
df_pit.to_csv("df_pit.csv", index=False)
```
