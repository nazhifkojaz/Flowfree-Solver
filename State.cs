using System.Collections.Generic;
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
  }

  private bool _preassigned;
  public bool Preassigned
  {
    get { return _preassigned; }
    set { _preassigned = value; }
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
}