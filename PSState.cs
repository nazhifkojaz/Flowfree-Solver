using System.Collections.Generic;
using System.Linq;
using System;
public class PSState
{
    private int _value;
    public int Value
    {
        get { return _value; }
        set { _value = value; }
    }
    
    private List<int> _domain;
    public List<int> Domain
    {
        get { return _domain; }
        set { _domain = value; }
    }
    
    private List<PSState> _peers = new List<PSState>();
    public List<PSState> Peers
    {
        get { return _peers; }
        set { _peers = value; }
    }
    private int _id;
    public int Id
    {
        get { return _id; }
        set { _id = value; }
    }
    private bool _active;
    public bool Active
    {
        get { return _active; }
        set { _active = value; }
    }
    
    
    public PSState(int id, bool active)
    {
        _id = id;
        _active = active;
    }
    
    public bool isConstraintsValid()
    {
        if(Value != -1)
        {
            int assignedWithSameValue = 0, unassigned = 0;
            foreach (var peer in _peers)
            {
                if(peer.Value == Value) assignedWithSameValue++;
                else if(peer.Value == -1) unassigned++;
            }
            
            if(_active && assignedWithSameValue > 1) return false;
            else if(_active && assignedWithSameValue < 1 && unassigned == 0) return false;
            else if(!_active && assignedWithSameValue > 2 && unassigned == 0) return false;
            else if(!_active && assignedWithSameValue < 2 && unassigned == 0) return false;
        }
        return true;
    }
    
    public List<PSState> GetUnassignedPeers()
    {
        List<PSState> unassigned = new List<PSState>();
        foreach (var peer in _peers)
        {
            if(peer.Value == -1) unassigned.Add(peer);
        }
        return unassigned;
    }
    
    
    
}