using System;
using System.Collections.Generic;
using System.Linq;

public static class Constants
{
    public const int MaxValue = 10000000;
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
    

    private List<TreeNode> _child;
    public List<TreeNode> Child
    {
        get { return _child; }
        set { _child = value; }
    }

    public TreeNode(bool isRoot)
    {
        if(isRoot)
        {
            _root = true;
            _pn = 0;
            _dn = 0;
            _child.Clear();
        }
    }

    public TreeNode(double nPN, double nDN)
    {
        _root = false;
        _pn = nPN;
        _dn = nDN;
        _child.Clear();
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