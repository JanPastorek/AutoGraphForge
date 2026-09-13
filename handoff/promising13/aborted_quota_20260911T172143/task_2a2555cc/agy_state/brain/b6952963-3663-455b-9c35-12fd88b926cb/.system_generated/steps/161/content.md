Title: Lower bounds for the total (distance) 𝑘-domination number of a graph

Source: https://arxiv.org/html/2406.08770

---

##### Report GitHub Issue
Content selection saved. Describe the issue below:
[Learn more](https://info.arxiv.org/about)
[Back to arXiv](https://arxiv.org/)
[Why HTML?](https://info.arxiv.org/about/accessible_HTML.html)
[Report Issue](https://arxiv.org/html/2406.08770)
[Back to Abstract](https://arxiv.org/abs/2406.08770v1)
[Download PDF](https://arxiv.org/pdf/2406.08770v1)
1. [Abstract](https://arxiv.org/html/2406.08770#abstract1)
2. [1 Introduction](https://arxiv.org/html/2406.08770#S1)
3. [2 Preliminaries](https://arxiv.org/html/2406.08770#S2)
4. [3 Lower Bounds for γkt​(G)\gamma_{k}^{t}(G)](https://arxiv.org/html/2406.08770#S3)
5. [References](https://arxiv.org/html/2406.08770#bib)
[Abstract](https://arxiv.org/html/2406.08770#abstract1)
[1 Introduction](https://arxiv.org/html/2406.08770#S1)
[2 Preliminaries](https://arxiv.org/html/2406.08770#S2)
[3 Lower Bounds for γkt​(G)\gamma_{k}^{t}(G)](https://arxiv.org/html/2406.08770#S3)
[References](https://arxiv.org/html/2406.08770#bib)
[License: CC BY 4.0](https://info.arxiv.org/help/license/index.html#licenses-available)

###### Abstract
For k≥1k\geq 1 and a graph GG without isolated vertices, a total (distance) kk-dominating set of GG is a set of vertices S⊆V⁡(G)S\subseteq V(G) such that every vertex in GG is within distance kk to some vertex of SS other than itself. The total (distance) kk-domination number of GG is the minimum cardinality of a total kk-dominating set in GG, and is denoted by γkt​(G)\gamma_{k}^{t}(G). When k=1k=1, the total kk-domination number reduces to the total domination number, written γt​(G)\gamma_{t}(G); that is, γt​(G)=γ1t​(G)\gamma_{t}(G)=\gamma_{1}^{t}(G). This paper shows that several known lower bounds on the total domination number generalize nicely to lower bounds on total (distance) kk-domination.
Keywords: Total distance kk-domination; total domination. AMS subject classification: 05C69

Distance domination in graphs is a well-known concept, with a recent survey estimating that there are more than 100 papers on the topic to date, including a chapter in the domination monograph by Haynes, Hedetniemi, and Henning [[6](https://arxiv.org/html/2406.0[8](https://arxiv.org/html/2406.08770#bib.bib8)770#bib.bib6)]. This paper considers a specific, widely applicable variant of distance domination called total distance kk-domination, and from hereon, referred to as total kk-domination for simplicity. This concept was introduced by Henning, Oellermann, and Swart in [[9](https://arxiv.org/html/2406.08770#bib.bib9)], where they define a total kk-dominating set of a graph GG to be a set S⊆V⁡(G)S\subseteq V(G) of vertices so that every vertex is within distance kk from some vertex of SS other than itself. More specifically, let k≥1k\geq 1 be an integer. A set S⊆V⁡(G)S\subseteq V(G) is total kk-dominating in GG if for every vertex v∈V⁡(G)v\in V(G), we have dG​(v,S∖{v})≤kd_{G}(v,S\setminus\{v\})\leq k. The total kk-domination number of GG is the cardinality of a minimum total kk-dominating set in GG and is denoted by γkt​(G)\gamma_{k}^{t}(G). A total kk-dominating set of GG with cardinality γkt​(G)\gamma_{k}^{t}(G) is called a γkt\gamma_{k}^{t}-set of GG. Since every vertex vv of GG must be within distance kk to some vertex different from vv in a total kk-dominating set, we note that total kk-domination is not defined for any graph with isolated vertices. We further remark that when k=1k=1, total kk-domination reduces to a well-known and heavily studied notion of total domination. In particular, we note that γt​(G)=γ1t​(G)\gamma_{t}(G)=\gamma_{1}^{t}(G), where γt​(G)\gamma_{t}(G) is the total domination number of GG. For more on total domination, see the excellent monograph by Henning and Yeo [8].
As with the total domination number of a graph, the computation of the total kk-domination number is NP-hard [[6](https://arxiv.org/html/2406.08770#bib.bib6)]. For this reason, many of the results on the total kk-domination have focused primarily on finding tight upper and lower bounds. For example, the upper bound of Henning, Oellermann, and Swart [[9](https://arxiv.org/html/2406.08770#bib.bib9)], which states that γkt​(G)≤2​n2​k+1\gamma_{k}^{t}(G)\leq\frac{2n}{2k+1}, whenever GG is a connected graph with order n≥2​k+1≥[3](https://arxiv.org/html/2406.08770#bib.bib3)n\geq 2k+1\geq 3. However, there do not seem to be many well-known lower bounds for the total kk-domination number in the literature, which differs from that of the non-total distance dominating variant [3]. This observation motivates our contributions. In particular, we extend several known lower bounds on the total domination number to lower bounds on the total kk-domination number.
Notation and Terminology. In this paper, we only consider finite and simple graphs. Let GG be a graph with vertex set V⁡(G)V(G) and edge set E⁡(G)E(G). The order and size of GG will be denoted by n⁡(G)=|V⁡(G)|n(G)=|V(G)| and m⁡(G)=|E⁡(G)|m(G)=|E(G)|, respectively. A nontrivial graph is a graph of order at least 2. Two vertices v,w∈V⁡(G)v,w\in V(G) are neighbors or adjacent whenever v​w∈E⁡(G)vw\in E(G). The open neighborhood of a vertex v∈V⁡(G)v\in V(G), written NG​(v)N_{G}(v), is the set of all neighbors of vv, whereas the closed neighborhood of vv is NG​[v]=NG​(v)∪{v}N_{G}[v]=N_{G}(v)\cup\{v\}. The degree of a vertex v∈V⁡(G)v\in V(G), written dG​(v)d_{G}(v), is the number of neighbors of vv in GG; and so, dG​(v)=|NG​(v)|d_{G}(v)=|N_{G}(v)|. A subgraph HH of GG is a graph where V⁡(H)⊆V⁡(G)V(H)\subseteq V(G) and E⁡(H)⊆E⁡(G)E(H)\subseteq E(G). If HH is a subgraph of GG, we write H⊆GH\subseteq G. The complete graph, path, and cycle on nn vertices will be denoted by KnK_{n}, PnP_{n}, and CnC_{n}, respectively.

A graph GG is connected if, for all vertices vv and ww in GG, a (v,w)(v,w)-path exists. A tree is a connected graph that contains no cycle as a subgraph. A forest is any graph that does not contain a cycle as a subgraph. If a forest is connected, it is necessarily a tree; if not, it is a disjoint union of trees called its components. A vertex of degree 1 in a tree is called a leaf, and a vertex with a leaf neighbor is a support vertex. The distance from a vertex vv to a vertex ww in GG, denoted dG​(v,w)d_{G}(v,w), is the length of a shortest (v,w)(v,w)-path in GG. The distance from a vertex vv to a set S⊆V⁡(G)S\subseteq V(G), denoted dG​(v,S)d_{G}(v,S), is the length of a shortest (v,w)(v,w)-path for all w∈Sw\in S. A vertex vv is said to kk-dominate a vertex ww different than vv if the distance from vv to ww is at most kk. The eccentricity of v∈Gv\in G, written eccG​(v){\rm ecc}_{G}(v) is the distance between vv and a vertex farthest from vv in GG. The minimum eccentricity among all vertices of GG is the radius of GG, denoted by rad⁡(G){\rm rad}(G), while the maximum eccentricity among all vertices of GG is the diameter of GG, denoted by diam⁡(G){\rm diam}(G). Thus, the diameter of GG is the maximum distance among all pairs of vertices of GG. A vertex vv with eccG​(v)=diam​(G){\rm ecc}_{G}(v)={\rm diam}(G) is called a peripheral vertex of GG. A diametrical path in GG is the shortest path in GG whose length is equal to the graph’s diameter. Thus, a diametrical path is a path of length diam⁡(G){\rm diam}(G) joining two peripheral vertices of GG.
For notation and graph terminology not introduced here, we refer the reader to [[7](https://arxiv.org/html/2406.08770#bib.bib7)]. We will also use the standard notation [k]={1,…,k}[k]=\{1,\ldots,k\}.

In this section we provide tools fore our main results in the next section. To begin, recall that every total kk-dominating set of a spanning subgraph of the graph GG is a total kk-dominating set of GG, and thus, we immediately have the following proposition.

###### Proposition 1.
For k≥1k\geq 1, if HH is a spanning subgraph of a graph GG without isolated vertices, then
We now present our first generalization from total domination to total kk-domination. More specifically, recall that in 2007 DeLaViña et al. [[4](https://arxiv.org/html/2406.08770#bib.bib4)] showed every non-trivial connected graph GG has a spanning tree TT satisfying γt​(G)=γt​(T)\gamma_{t}(G)=\gamma_{t}(T). This result generalizes from total domination to total kk-domination, as shown by the following lemma.

###### Lemma 2.
For k≥1k\geq 1, if GG is a connected graph of order n≥2n\geq 2, then GG has spanning tree TT such that

###### Proof.
Let k≥1k\geq 1 and let GG be a connected graph of order n≥2n\geq 2. Next let S⊆V⁡(G)S\subseteq V(G) be a γkt\gamma_{k}^{t}-set of GG. Thus, every vertex vv of GG is within distance to kk to the set S∖{v}S\setminus\{v\} and γkt​(G)=|S|\gamma_{k}^{t}(G)=|S|. For each i∈[k]i\in[k], define the set DiD_{i} to be the set of all vertices v∈V⁡(G)v\in V(G) for which dG​(v,S∖{v})=id_{G}(v,S\setminus\{v\})=i; that is,
Since SS is a total kk-dominating set of GG, every vertex v∈V⁡(G)v\in V(G) belongs to some DiD_{i} for i∈[k]i\in[k]. Moreover, if v∈Div\in D_{i}, then vv has at least 1 neighbor in Di−1D_{i-1}, since otherwise vv would not be at distance ii with S∖{v}S\setminus\{v\}. Note that it is also possible that if v∈Div\in D_{i}, then vv could have neighbors in DiD_{i} and Di+1D_{i+1}. We next construct a spanning subgraph F⊆GF\subseteq G as follows. For each i∈[k]i\in[k], apply the following rules:
- 1. 

For each vertex v∈Div\in D_{i}, delete all but 1 of the edges joining vv to the set Di−1D_{i-1}.

- 2. 

For each vertex v∈Div\in D_{i}, delete all edges, if any, that join vv to other vertices in the set DiD_{i}.

For each vertex v∈Div\in D_{i}, delete all but 1 of the edges joining vv to the set Di−1D_{i-1}.
For each vertex v∈Div\in D_{i}, delete all edges, if any, that join vv to other vertices in the set DiD_{i}.
Since we did not delete any vertices in the above steps, we note that FF is a spanning subgraph of GG. We next show that FF is necessarily a spanning forest of GG.

###### Claim 1.
The subgraph FF is a spanning forest.

###### Proof.
By way of contradiction, suppose that FF is not a forest. Thus, FF contains at least one cycle as a subgraph. Let CC be one such cycle in FF and let vv be a vertex of CC of maximum distance (noninclusive) to the set SS in GG; that is, dG​(v,S∖{v})≥dG​(w,S∖{w})d_{G}(v,S\setminus\{v\})\geq d_{G}(w,S\setminus\{w\}) for all w∈Sw\in S. Suppose now that dG​(v,S∖{v})=ℓd_{G}(v,S\setminus\{v\})=\ell, and so, v∈Dℓv\in D_{\ell}. If there were a vertex ww on CC with dG​(w,S∖{w})>ℓd_{G}(w,S\setminus\{w\})>\ell, then vv would not be a vertex of CC at maximum (noninclusive) distance from SS, a contradiction. Thus, dG​(w,S∖{w})≤ℓd_{G}(w,S\setminus\{w\})\leq\ell for all vertices ww in CC.
Let v1v_{1} and v2v_{2} be the 2 neighbors of vv on the cycle CC. Next recall that when constructing FF from GG, we removed any edges connecting vv to other vertices in DℓD_{\ell}. Thus, v1v_{1} and v2v_{2} cannot be elements of the set DℓD_{\ell}. Hence, the neighbors v1v_{1} and v2v_{2} of vv on CC are both elements of the set Dℓ−1D_{\ell-1}, a contradiction since vv will have at most one neighbor in the set Dℓ−1D_{\ell-1} by construction of FF. Therefore, FF cannot contain a cycle as a subgraph, and so, FF is a spanning forest of GG. (□\Box)

We now construct a spanning tree TT from FF as follows. If FF is a tree, then let T=FT=F. Otherwise, FF is a disjoint union of ℓ\ell tree components for some ℓ≥2\ell\geq 2. In the case that FF consists of ℓ\ell components, we let TT be the tree obtained from FF by adding to FF ℓ−[1](https://arxiv.org/html/2406.08770#Thmthm1)\ell-1 so that the resulting graph TT is connected. Note that TT is necessarily a spanning tree of GG. Moreover, for i∈[k]i\in[k] and v∈V⁡(G)v\in V(G), if v∈Div\in D_{i}, then there is a path from vv to S∖{v}S\setminus\{v\} of length ii in TT, and so, dT​(v,S∖{v})≤dG​(v,S∖{v})d_{T}(v,S\setminus\{v\})\leq d_{G}(v,S\setminus\{v\}). However, TT is a spanning subgraph of GG, which implies dG​(v,S∖{v})≤dT​(v,S∖{v})d_{G}(v,S\setminus\{v\})\leq d_{T}(v,S\setminus\{v\}) for all v∈V⁡(G)v\in V(G). Thus, TT is a spanning tree of GG that is distance-preserving from SS, in the sense that dT​(v,S∖{v})=dG​(v,S∖{v})d_{T}(v,S\setminus\{v\})=d_{G}(v,S\setminus\{v\}) for all v∈V⁡(G)v\in V(G). It follows that since SS is a total kk-dominating set of GG, it must be that SS is also a total kk-dominating set of TT. Thus, γkt​(T)≤|S|=γkt​(G)\gamma_{k}^{t}(T)\leq|S|=\gamma_{k}^{t}(G). However, Proposition 1 states γkt​(G)≤γkt​(T)\gamma_{k}^{t}(G)\leq\gamma_{k}^{t}(T). Hence, γkt​(G)=γkt​(T)\gamma_{k}^{t}(G)=\gamma_{k}^{t}(T). ∎

In this section we generalize several known lower bounds for the total domination number to those for the total kk-domination number. To begin, recall that for k≥1k\geq 1, the kk-neighborhood of a vertex v∈V⁡(G)v\in V(G) is the set of all vertices different from vv that are at distance at most kk to vv; that is, NG,k​(v)={w:1≤dG​(v,w)≤k}N_{G,k}(v)=\{w:1\leq d_{G}(v,w)\leq k\}. The kk-degree of a vertex v∈V⁡(G)v\in V(G) is defined as dG,k​(v)=|NG,k​(v)|d_{G,k}(v)=|N_{G,k}(v)|. The maximum kk-degree and minimum kk-degree of a graph GG are denoted Δk​(G)\Delta_{k}(G) and δk​(G)\delta_{k}(G), respectively. The kk-degree sequence of GG is the list of all vertex kk-degree’s of GG in nonincreasing order and is written Dk​(G)=(Δk​(G)=dk1,…,dkn=δk​(G))D_{k}(G)=\Big(\Delta_{k}(G)=d_{k}^{1},\dots,d_{k}^{n}=\delta_{k}(G)\Big).
For k≥1k\geq 1 and a graph GG of order nn, we define the sub-total (distance) kk-domination number of GG, written subkt​(G)\mathrm{sub}_{k}^{t}(G), as the smallest integer jj such that dk1+⋯+dkj≥nd_{k}^{1}+\dots+d_{k}^{j}\geq n; that is,
When k=[1](https://arxiv.org/html/2406.08770#bib.bib1)k=1, the sub-total kk-domination number reduces to the sub-total domination number, written subt​(G)\mathrm{sub}_{t}(G) and introduced by Davila in [[[2](https://arxiv.org/html/2406.08770#bib.bib2)](https://arxiv.org/html/2406.08770#bib.bib2)], and simultaneously introduced by Gentner and Rautenbach in [[[5](https://arxiv.org/html/2406.08770#bib.bib5)](https://arxiv.org/html/2406.08770#bib.bib5)], where they adopt the notation s​lt​(G)sl_{t}(G) to emphasize the connection to the well-known Slater number of a graph [[10](https://arxiv.org/html/2406.08770#bib.bib10)]. Regardless of notation, subt​(G)\mathrm{sub}_{t}(G) (and s​lt​(G)sl_{t}(G)) serve as simple lower bounds for the total domination number. That is, γt​(G)≥subt​(G)\gamma_{t}(G)\geq\mathrm{sub}_{t}(G) for any isolate-free graph GG [2, 5]; which is notably a simple application of the degree sequence index strategy (DSI-strategy) formally introduced by Caro and Pepper in [1]. The following theorem shows that this bound can easily be generalized from total domination to one for total kk-domination.

###### Theorem 3.
For k≥1k\geq 1, if GG is a isolate-free graph, then

###### Proof.
Let k≥1k\geq 1 and let GG be an isolate-free graph of order nn. Next let j=subkt​(G)j=\mathrm{sub}_{k}^{t}(G) and let S⊆V⁡(G)S\subseteq V(G) be a γkt\gamma_{k}^{t}-set of GG. Thus, every vertex vv of GG is within distance to kk to the set S∖{v}S\setminus\{v\} and γkt​(G)=|S|\gamma_{k}^{t}(G)=|S|. Hence, V⁡(G)=⋃v∈SNG,k​(v)V(G)=\bigcup_{v\in S}N_{G,k}(v). Therefore,
and so, ∑v∈SdG,k​(v)≥n\sum_{v\in S}d_{G,k}(v)\geq n. Since the sum of the kk-degrees from the vertices in SS is at most the sum of the first |S||S| entries from the kk-degree sequence Dk​(G)D_{k}(G), we obtain the following inequality,
Since jj is the smallest integer satisfying ∑i=1jdki≥n\sum_{i=1}^{j}d_{k}^{i}\geq n, it follows that
and the desired inequality is established. ∎
A trivial lower bound for the total domination number of any isolate-free graph of order n≥2n\geq 2 and maximum degree Δ\Delta is γt​(G)≥nΔ\gamma_{t}(G)\geq\frac{n}{\Delta}. As a simple application of Theorem [3](https://arxiv.org/html/2406.08770#Thmthm3), we next show that this lower bound on the total domination number also generalizes to a bound for the total kk-domination number.

###### Corollary 4.
For k≥1k\geq 1, if GG is an isolate-free graph with order nn and maximum kk-degree Δk\Delta_{k}, then

###### Proof.
Let GG be an isolate-free graph of order nn and maximum kk-degree Δk\Delta_{k}. Next let j=subkt​(G)j=\mathrm{sub}_{k}^{t}(G), and note that Theorem [3](https://arxiv.org/html/2406.08770#Thmthm3) implies γkt​(G)≥j\gamma_{k}^{t}(G)\geq j. For each i∈[n]i\in[n] observe that dki≤Δkd_{k}^{i}\leq\Delta_{k}. Thus, we obtain the following chain of inequalities,
Hence,
and the desired bound is established. ∎
In [[4](https://arxiv.org/html/2406.08770#bib.bib4)] DeLaViña et al. proved γt​(G)≥12​(diam⁡(G)+1)\gamma_{t}(G)\geq\frac{1}{2}({\rm diam}(G)+1) for any connected graph GG of order n≥2n\geq 2. The following theorem extends this lower bound from the total domination number to a lower bound on the total kk-domination number.

###### Theorem 5.

For k≥1k\geq 1, if GG is a connected graph of order n≥2n\geq 2, then

###### Proof.
Let GG be a connected graph with order n≥2n\geq 2 and let d=diam⁡(G)d={\rm diam}(G). Let P:u0​u1​…​udP:u_{0}u_{1}\ldots u_{d} be a diametrical path in GG, joining two peripheral vertices u=u0u=u_{0} and v=udv=u_{d} of GG, and so, dG​(u,v)=dd_{G}(u,v)=d and let SS be a γkt\gamma_{k}^{t}-set of GG of GG. Thus, every vertex vv of GG is within distance to kk to the set S∖{v}S\setminus\{v\} and γkt​(G)=|S|\gamma_{k}^{t}(G)=|S|. We proceed by first proving the following claim about the number of vertices of PP that any vertex of SS may kk-dominate.

###### Claim 2.
Any vertex of SS will kk-dominate at most 2​k2k vertices in PP.

###### Proof.
Let q∈Sq\in S be a vertex of SS that kk-dominates at least one vertex from the path PP. Next let QQ be the set of all vertices in PP that are kk-dominated by qq and then let ii and jj be the smallest and largest integers in the set [d][d], respectively, such that ui∈Qu_{i}\in Q and uj∈Qu_{j}\in Q. Since every vertex of QQ is a vertex in the path PP and since we choose a smallest integer ii with ui∈Qu_{i}\in Q, and largest integer jj with uj∈Qu_{j}\in Q, it must be the case that Q⊆{ui,ui+1,…,uj}Q\subseteq\{u_{i},u_{i+1},\ldots,u_{j}\}.
Let P′:ui​…​djP^{\prime}:u_{i}\dots d_{j} be the path subgraph of PP connecting uiu_{i} to uju_{j} in PP and note that since PP is a shortest (u,v)(u,v)-path in GG, it must be the case that P′P^{\prime} is a shortest (ui,uj)(u_{i},u_{j})-path in GG. Next let PiP_{i} be a shortest (ui,q)(u_{i},q)-path in GG and let PjP_{j} be a shortest (q,uj)(q,u_{j})-path in GG, and observe that since qq will kk-dominate both uiu_{i} and uju_{j} in GG, both paths PiP_{i} and PjP_{j} have at length most kk. Therefore, the (ui,uj)(u_{i},u_{j})-path, say P′′P^{\prime\prime}, obtained by following the path PiP_{i} from uiu_{i} to qq, and then proceeding along the path PjP_{j} from qq to uju_{j}, has length at most 2​k2k, for otherwise, the vertices uiu_{i} and uju_{j} on the path PP would not be the vertices with minimum and maximum indices so that ui∈Qu_{i}\in Q and uj∈Qu_{j}\in Q, respectively. Thus, P′′P^{\prime\prime} has order at most 2​k+12k+1. Since qq does not kk-dominate itself, qq will kk-dominate at most (2​k+1)−1=2​k(2k+1)-1=2k vertices on P′′P^{\prime\prime}, which in-turn implies that qq will kk-dominate at most 2​k2k vertices on P′P^{\prime}. Since Q⊆V⁡(P′)Q\subseteq V(P^{\prime}), qq will kk-dominate at most 2​k2k vertices in the path PP. (□\Box)
By Claim [2](https://arxiv.org/html/2406.08770#Thmclaim2), each vertex in SS will kk-dominate at most 2​k2k vertices of the diametrical path PP. Further, since PP has d+1d+1 vertices, we observe 2​k​|S|≥d+12k|S|\geq d+1. Hence,
and the desired bound is established. ∎
Another bound for the total domination number is γt​(G)≥rad⁡(G)\gamma_{t}(G)\geq{\rm rad}(G) [[4](https://arxiv.org/html/[2](https://arxiv.org/html/2406.08770#Thmthm2)406.08770#bib.bib4)]. We generalize this radius lower bound for the total domination number to a lower bound for the total kk-domination number by applying Theorem [5](https://arxiv.org/html/2406.08770#Thmthm5) and Lemma 2.

###### Theorem 6.
For k≥1k\geq 1, if GG is a connected graph of order n≥2n\geq 2, then

###### Proof.
Let k≥1k\geq 1 and let GG be a connected graph of order n≥[2](https://arxiv.org/html/2406.08770#Thmthm2)n\geq 2. By Lemma 2, GG has a spanning tree TT such that γkt​(G)=γkt​(T)\gamma_{k}^{t}(G)=\gamma_{k}^{t}(T). Adding edges to TT will not increase the radius, and so rad⁡(G)≤rad⁡(T){\rm rad}(G)\leq{\rm rad}(T). Moreover, since TT is a tree, diam⁡(T)≥2​rad​(T)−1{\rm diam}(T)\geq 2{\rm rad}(T)-1. Thus, by applying Theorem [5](https://arxiv.org/html/2406.08770#Thmthm5), we obtain the following chain of inequalities,
Hence, γkt​(G)≥1k​rad​(G)\gamma_{k}^{t}(G)\geq\frac{1}{k}{\rm rad}(G), and the desired bound is established. ∎

## References
- [1]
 Y. Caro and R. Pepper, Degree sequence index strategy, Australas. J. Comb., 59(1) (2014), 1–23.


- [2]
 R. Davila, A note on the sub-total domination number of a graph, ArXiv Preprint: arXiv:1701.07811 (2017).


- [3]
 R. Davila, C. Fast, M. A. Henning, and F. Kenter, Lower bounds on the distance domination number of a graph, Contrib. Discrete Math., 12 (2017), 476–485.


- [4]
 E. DeLaViña, Q. Liu, R. Pepper, B. Waller, and D. B. West, Some conjectures of Graffiti.pc on total domination, Congressus Numer., 185 (2007), 81–95.


- [5]
 M. Gentner and D. Rautenbach, Some comments on the Slater number, Discrete Math., 340(7) (2017), 1497–1502.


- [6]
 T. Haynes, S. Hedetniemi, and M. A. Henning, Topics in Domination in Graphs (Springer Developments in Mathematics, 64). ISBN: 978-3-031-09495-8 (2021).


- [7]
 T. Haynes, S. Hedetniemi, and M. A. Henning, Domination in Graphs: Core Concepts (Springer Monographs in Mathematics). ISBN: 978-3-031-09495-8 (2023).


- [8]
 M. A. Henning and A. Yeo, Total Domination in Graphs (Springer Monographs in Mathematics). ISBN: 978-1-4614-6524-9 (2010).


- [9]
 M. A. Henning, O. R. Oellermann, and H. C. Swart, Bounds on distance domination parameters, J. Combin. Comput. Inf. Sys. Sciences 16 (1991), 11–18.


- [10]
 P. J. Slater, Locating dominating sets and locating-dominating sets. Graph Theory, Combinatorics, and Algorithms, Vol. 1, 2(Kalamazoo, MI 1992), 1073–1079. Wiley-Intersci. Publ. (Wiley, New York, 1995)


[view the build logs](https://arxiv.org/html/2406.08770v1/__stdout.txt)
[L
        A
        T
        E

      xml](https://math.nist.gov/~BMiller/LaTeXML/)

## Instructions for reporting errors
We are continuing to improve HTML versions of papers, and your feedback helps enhance accessibility and mobile support. To report errors in the HTML that will help us improve conversion and rendering, choose any of the methods listed below:
- Click the "Report Issue" (

          ) button, located in the page header.
Tip: You can select the relevant text first, to include it in your report.
Our team has already identified [the following issues](https://github.com/arXiv/html_feedback/issues). We appreciate your time reviewing and reporting rendering errors we may not have found yet. Your efforts will help us improve the HTML versions for all readers, because disability should not be a barrier to accessing research. Thank you for your continued support in championing open access for all.
Have a free development cycle? Help support accessibility at arXiv! Our collaborators at LaTeXML maintain a [list of packages that need conversion](https://github.com/brucemiller/LaTeXML/wiki/Porting-LaTeX-packages-for-LaTeXML), and welcome [developer contributions](https://github.com/brucemiller/LaTeXML/issues).
[member institutions](https://info.arxiv.org/about/ourmembers.html)
[About](https://info.arxiv.org/about)
[Help](https://info.arxiv.org/help)
[Contact](https://info.arxiv.org/help/contact.html)
[Subscribe](https://info.arxiv.org/help/subscribe)
[Copyright](https://info.arxiv.org/help/license/index.html)
[Privacy](https://info.arxiv.org/help/policies/privacy_policy.html)
[Accessibility](https://info.arxiv.org/help/web_accessibility.html)
[Operational Status (opens in new tab)](https://status.arxiv.org)

