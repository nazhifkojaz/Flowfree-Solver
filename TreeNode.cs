using System;
using System.Collections.Generic;
using System.Linq;

public static class Constants
{
    public const int MaxValue = 10000000;
    public enum NodeType
    {
        unknown, proof, disproof
    };
}

public class TreeNode
{
    private int _index;
    public int Index
    {
        get { return _index; }
        set { _index = value; }
    }
    
    private double _pn;
    public double Pn
    {
        get { return _pn; }
        set { _pn = value; }
    }
    private double _dn;
    public double Dn
    {
        get { return _dn; }
        set { _dn = value; }
    }
    private bool _root;
    public bool Root
    {
        get { return _root; }
        set { _root = value; }
    }

    private TreeNode _parent;
    public TreeNode Parent
    {
        get { return _parent; }
        set { _parent = value; }
    }
    
    private Constants.NodeType _nodeType;
    public Constants.NodeType NodeType
    {
        get { return _nodeType; }
        set { _nodeType = value; }
    }

    private List<TreeNode> _child = new List<TreeNode>();
    public List<TreeNode> Child
    {
        get { return _child; }
        set { _child = value; }
    }
    private bool _isAnd;
    public bool IsAnd
    {
        get { return _isAnd; }
        set { _isAnd = value; }
    }

    private int _cVal;
    public int CVal
    {
        get { return _cVal; }
        set { _cVal = value; }
    }
    
    
    

    public TreeNode(bool isRoot)
    {
        if(isRoot)
        {
            _isAnd = false;
            _root = true;
            _pn = 0;
            _dn = 0;
            _child.Clear();
            _nodeType = Constants.NodeType.proof;
        }
    }

    public TreeNode(double nPN, double nDN)
    {
        _isAnd = true;
        _root = false;
        _pn = nPN;
        _dn = nDN;
        _child.Clear();
        _nodeType = Constants.NodeType.unknown;
    }

    public void PrintChild()
    {
        foreach (var ch in _child)
        {
            Console.WriteLine($"child index - {ch._index}");
            if(ch.Child.Count > 0) ch.PrintChild();
        }
    }
    
    
}