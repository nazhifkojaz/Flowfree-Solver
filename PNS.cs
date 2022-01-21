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
    
    
    public PNS()
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
    }
}