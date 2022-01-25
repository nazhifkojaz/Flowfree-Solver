using System;
using System.Collections.Generic;
using System.Linq;

public class PNS
{
    private TreeNode _best;
    public TreeNode Best
    {
        get { return _best; }
        set { _best = value; }
    }
    private TreeNode _root;
    public TreeNode Root
    {
        get { return _root; }
        set { _root = value; }
    }
    private TreeNode _curNode;
    public TreeNode CurNode
    {
        get { return _curNode; }
        set { _curNode = value; }
    }
    private int _nodeNum;
    public int NodeNum
    {
        get { return _nodeNum; }
        set { _nodeNum = value; }
    }
    private bool _solved;
    public bool Solved
    {
        get { return _solved; }
        set { _solved = value; }
    }

    private Board _problem;
    public Board Problem
    {
        get { return _problem; }
        set { _problem = value; }
    }


    public PNS(Board problem)
    {
        _root = new TreeNode(true);
        _root.Index = 0;
        _root.Pn = 0;
        _root.Dn = 0;
        _root.Child.Clear();
        _best = null;
        _curNode = null;
        _nodeNum = 0;
        _solved = false;
        _problem = problem;

        search(_root); //pake ref
        // int pn = 0, dn = 0, un = 0;
        // TraverseNode(ref pn, ref dn, ref un, _root);
        // TraverseFinal(finalNode);
        // Console.WriteLine($"pn node = {pn}, dn node = {dn}, un node={un}");
    }

    public void TraverseNode(ref int pn, ref int dn, ref int un, TreeNode node)
    {
        foreach (var child in node.Child)
        {
            switch (child.NodeType)
            {
                case Constants.NodeType.proof: pn++; Console.WriteLine($"proof index-{child.Index}"); break;
                case Constants.NodeType.disproof: dn++; Console.WriteLine($"disproof index-{child.Index}"); break;
                case Constants.NodeType.unknown: un++; Console.WriteLine($"unknown index-{child.Index}"); break;
                default: break;
            }
            if (child.Child.Count > 0) TraverseNode(ref pn, ref dn, ref un, child);
        }
    }

    public void TraverseFinal(TreeNode node)
    {
        Console.WriteLine($"node index = {node.Index}");
        if (node.Parent != null) TraverseFinal(node.Parent);
    }

    public bool search(TreeNode p) //pake ref
    {
        // finished scenario
        if (_problem.IsAssigned() && _problem.GetBoardString() == _problem.CompleteBoard) return true;
        else
        {
            GenerateChild(p); //pake ref
            //iterate through active states
            // .OrderBy(o => o.GetUnassignedPeers().Count).ToList();
            foreach (var current in p.Child.OrderBy(o => o.Pn).ToList()) // get the child based on least number of pn first
            // foreach (var current in _problem.GetActiveStatesOrdered())
            // foreach (var current in _problem.GetActiveStates()) //this is without MRV
            {
                current.NodeType = Constants.NodeType.proof;
                SetProofAndDisproofNumber(current); //pake ref
                _problem.States[current.Index].Active = false;

                GenerateNeighbor(current); //pake ref
                //iterate through current state's unassigned peers
                //this part can also be categorized as 'forward checking', right?
                foreach (var peer in current.Child.OrderBy(o => o.Pn).ToList()) // get the peer based on least number of pn
                // foreach (var peer in current.GetUnassignedPeersOrdered(_problem.GetColorPair(current.Id, current.Value), _problem.Width))
                // foreach (var peer in current.GetUnassignedPeers())
                {
                    peer.NodeType = Constants.NodeType.proof;
                    UpdateAncestor(peer); //pake ref

                    _problem.States[peer.Index].Active = true;
                    _problem.States[peer.Index].Value = _problem.States[current.Index].Value;
                    _problem.NodesCount++;

                    if (_problem.IsValid())
                    {
                        if (search(peer)) return true; //pake ref
                    }

                    _problem.States[peer.Index].Active = false;
                    _problem.States[peer.Index].Value = -1;
                    peer.NodeType = Constants.NodeType.disproof;
                    UpdateAncestor(peer); //pake ref
                }

                current.NodeType = Constants.NodeType.disproof;
                _problem.States[current.Index].Active = false;
            }
        }
        // Console.WriteLine("failed");
        return false;
    }

    public void UpdateAncestor(TreeNode n) //pake ref
    {
        while (n != _root)
        {
            double oldPn = n.Pn, oldDn = n.Dn;
            SetProofAndDisproofNumber(n); //pake ref
            if (n.Pn == oldPn && n.Dn == oldDn) return;
            n = n.Parent;
        }
        SetProofAndDisproofNumber(_root); //pake ref
    }

    public void SetProofAndDisproofNumber(TreeNode n) //pake ref
    {
        if (n.Child.Count > 0)
        {
            if (n.IsAnd)
            {
                n.Pn = 0; n.Dn = Constants.MaxValue;
                for (int i = 0; i < n.Child.Count; i++)
                {
                    n.Pn += n.Child[i].Pn;
                    n.Dn = Math.Min(n.Dn, n.Child[i].Dn);
                }
            }
            else
            {
                n.Pn = Constants.MaxValue; n.Dn = 0;
                for (int i = 0; i < n.Child.Count; i++)
                {
                    n.Dn += n.Child[i].Dn;
                    n.Pn = Math.Min(n.Pn, n.Child[i].Pn);
                }
            }
        }
        else
        {
            switch (n.NodeType)
            {
                case Constants.NodeType.proof: n.Pn = 0; n.Dn = Constants.MaxValue; break;
                case Constants.NodeType.disproof: n.Pn = Constants.MaxValue; n.Dn = 0; break;
                case Constants.NodeType.unknown: n.Pn = 1; n.Dn = 1; break;
                default: break;
            }
        }
    }

    public void GenerateChild(TreeNode p) //pake ref
    {
        foreach (var node in _problem.GetActiveStates())
        {
            TreeNode childNode = new TreeNode(1, 1);
            childNode.Index = node.Id;
            p.Child.Add(childNode);
            childNode.Parent = p;
        }
        SetProofAndDisproofNumber(p); //pake ref
    }

    public void GenerateNeighbor(TreeNode p) //pake ref
    {
        foreach (var peer in _problem.States[p.Index].GetUnassignedPeers())
        {
            TreeNode childNode = new TreeNode(1, 1);
            childNode.Index = peer.Id;
            p.Child.Add(childNode);
            childNode.Parent = p;
        }
        SetProofAndDisproofNumber(p); //pake ref
    }
}