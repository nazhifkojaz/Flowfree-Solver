using System.Collections.Generic;
using System.Linq;
using System;
public class State
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

  private List<State> _peers = new List<State>();
  public List<State> Peers
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

  public State(int id, List<int> domain)
  {
    _id = id;
    _domain = domain;
    Value = -1;
    _active = false;
  }
  public State(int id)
  {
    _id = id;
    _value = -1;
    _active = false;
    _preassigned = false;
  }

  private bool _preassigned;
  public bool Preassigned
  {
    get { return _preassigned; }
    set { _preassigned = value; }
  }

  private bool _active;
  public bool Active
  {
      get { return _active; }
      set { _active = value; }
  }
  public int Top{get;set;}
  public int Bot{get;set;}
  public int Right{get;set;}
  public int Left{get;set;}
  

  public List<State> GetUnassignedPeers()
  {
    List<State> unassigned = new List<State>();
    foreach (var peer in _peers)
      if(peer.Value == -1) unassigned.Add(peer);

    return unassigned;
  }
  
  public List<State> GetInactivePeers()
  {
    List<State> inactives = new List<State>();
    foreach (var peer in _peers)
      if(!peer.Active) inactives.Add(peer);
    return inactives;
  }
  
  public List<State> GetUnassignedPeersOrdered(int id, int size)
  {
    List<State> unassigned = GetUnassignedPeers().OrderBy(o => o.GetDistance(id, size)).ToList();
    return unassigned;
  }
  // public List<State> GetActiveStatesOrdered()
  // {
  //   List<State> temp = GetActiveStates().OrderBy(o => o.GetUnassignedPeers().Count).ToList();
  //   // List<State> temp = GetActiveStates().OrderByDescending(o=>o.GetUnassignedPeers().Count).ToList();
  //   return temp;
  // }

  public Record MaintainDomains()
  {
    List<State> affectedPeers = new List<State>();
    if(Preassigned)
    {
      // we need at max one peer with the same value
      foreach (var peer in _peers)
      {
        if(peer.Value == _value)
        {
          // iterate through all other peers and remove the value from their domains if they are not assigned
          // if other peer is assigned with a value, that is equal to the current value, throw exception
          foreach (State otherPeer in _peers.Select(i => i).Where(i => i.Id != peer.Id).ToList())
          {
            if(otherPeer.Value == _value) throw new System.Exception("we are not supposed to find this, too many same value peers");
            else
            {
              otherPeer.Domain.Remove(_value);
              affectedPeers.Add(otherPeer);
            }
          }
        return new Record(_value, affectedPeers);
        }
      }
    }
    else
    {
      // we need at max 2 peers with the same value
      int idOne = -1, idTwo = -1;
      foreach (var peer in _peers)
      {
        if(peer.Value == _value && (idOne != -1 && idTwo != -1))
        {
          foreach (State otherPeer in _peers.Select(i => i).Where(i => (i.Id != idOne && i.Id != idTwo)).ToList())
          {
            if(otherPeer.Value == _value) throw new System.Exception("we are not supposed to find this, too many same value peers");
            else
            {
              otherPeer.Domain.Remove(_value);
              affectedPeers.Add(otherPeer);
            }
          }
          return new Record(_value, affectedPeers);
        }
        else if(peer.Value == _value && idOne != -1) idTwo = peer.Id;
        else if(peer.Value == _value) idOne = peer.Id;
      }
    }
    return null;
  }

  public bool IsConstraintsValid()
  {
    if (Value != -1)
    {
      int assignedWithSameValue = 0, unassigned = 0;
      foreach (var peer in Peers)
      {
        if (peer.Value == Value) assignedWithSameValue++;
        else if (peer.Value == -1) unassigned++;
      }

      if (Preassigned && assignedWithSameValue > 1) return false;
      else if(Preassigned && assignedWithSameValue < 1 && unassigned == 0) return false;
      else if(!Preassigned && assignedWithSameValue > 2 && unassigned == 0) return false;
      else if(!Preassigned && assignedWithSameValue < 2 && unassigned == 0) return false;
      // else if (assignedWithSameValue > 2) return false;
      // else if (unassigned == 0 && assignedWithSameValue == 0) return false;
      // else if (unassigned == 0 && assignedWithSameValue == 1 && !Preassigned) return false;
      // if unassigned is 1, assigned(same) is 1
    }

    return true;
  }
  public bool isConstraintsMet()
  {
    if (Active)
    {
      int assignedWithSameValue = 0, unassigned = 0;
      foreach (var peer in Peers)
      {
        if (peer.Value == Value && peer.Active) assignedWithSameValue++;
        else if (!peer.Active) unassigned++;
      }

      if (Preassigned && assignedWithSameValue > 1) return false;
      else if(Preassigned && assignedWithSameValue < 1 && unassigned == 0) return false;
      else if(!Preassigned && assignedWithSameValue > 2 && unassigned == 0) return false;
      else if(!Preassigned && assignedWithSameValue < 2 && unassigned == 0) return false;
      // else if (assignedWithSameValue > 2) return false;
      // else if (unassigned == 0 && assignedWithSameValue == 0) return false;
      // else if (unassigned == 0 && assignedWithSameValue == 1 && !Preassigned) return false;
      // if unassigned is 1, assigned(same) is 1
    }

    return true;
  }
  public int GetDistance(int target, int boardSize)
  {
    int x1, x2, y1, y2;
    x1 = _id % boardSize;
    y1 = _id / boardSize;
    x2 = _id % boardSize;
    y2 = _id / boardSize;
    
    return (Math.Abs(x1 - x2) + Math.Abs(y1 - y2));
  }
}