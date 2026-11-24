# Assignment 3

## Project

FinGuard scores Bitcoin transactions for fraud by treating payments as a graph and training a graph neural network, so a transaction is judged from the payments around it.

https://github.com/Md-hayath/FinGuard-GNN-Fraud-Detection

## Why it was hard

Fraud in this data is a pattern of payments, not a property of one row, so the model has to learn over 203,769 transactions and 234,355 edges.

The split has to be by time. A random split lets a test transaction sit next to training transactions from the future, the network passes information backward along that edge, and the score looks strong until you try it on new data.

About 2% of nodes are labelled illicit and about 77% have no label. Accuracy is the wrong metric here, and a gradient boosting model on the same features beat the graph network. Measuring that properly, and saying so, took longer than getting the network to train.

## How I approached it

Laundering shows up as movement. Money is gathered from many places, split, passed through a middle transaction, and sometimes sent back. A model that sees one transaction at a time misses that, so I used the public Elliptic Bitcoin dataset, which is the usual benchmark for this problem. A node is one transaction, with 165 anonymised features. An edge is bitcoin flowing from one transaction into another. The data is spread over 49 time steps of about two weeks each.

I built the graph in PyTorch Geometric and trained a two-layer GraphSAGE. GraphSAGE learns how to combine a node with its neighbours, and once it is trained it can score a transaction that was not in the training graph, which is what you need when new payments keep arriving. The network takes 170 inputs, uses two hidden layers of 128, and outputs one score per node. Five of those inputs are tags I compute from the edge list: fan-in, fan-out, a relay, a back-and-forth pair, and a short cycle. They describe the shape of the money movement, and the same tags are shown on each alert so an analyst can read them without looking at the weights.

Most of the graph is unlabelled. Unknown nodes stay in the graph, because messages still have to pass through them, but they are left out of the loss. Among the labelled nodes fraud is about one in ten, so plain cross-entropy spends its gradient on the easy licit cases. I trained with focal loss, which down-weights those once the model already gets them right. I stop training on validation AUC-PR. A model that always says licit is about 90% accurate on the labelled nodes and catches no fraud, so I also track precision in the top 100 alerts, and recall if an analyst can only review the top 5% of the queue.

Training uses time steps 1 to 30, validation uses 31 to 34, and the test set is step 35 onward. Validation AUC-PR is 0.885. Test AUC-PR is 0.558. The drop is a real shift in the later windows, including a darknet market shutdown, and published models on this dataset drop there too. Precision in the top 100 alerts on the test set is 0.87, which is the figure that matters if someone works the queue from the top.

I then trained logistic regression and gradient boosting on the same 170 features, with no message passing, on the same time split.

| model | test AUC-PR | precision at top 100 | F1 |
|---|---:|---:|---:|
| logistic regression | 0.22 | 0.07 | 0.37 |
| gradient boosting | 0.80 | 1.00 | 0.81 |
| GraphSAGE | 0.56 | 0.87 | 0.58 |

Gradient boosting wins. That is the known result on Elliptic, and the reason is in the features: 72 of the original 165 columns are already summaries of a node's neighbours, so a tree model receives a lot of the graph signal in the table. A graph network earns its place when a node's own features are weak, when the pattern spans more than one hop, and when the node did not exist at training time. That is the dataset I would move to next, along with a score on the edge itself so one transfer can be flagged.

The last part is the alert a person has to read. A small Streamlit app ranks transactions by score. Open one and it draws the neighbourhood, shows which inputs pushed the score up, and lists the neighbours the model scored as risky.
