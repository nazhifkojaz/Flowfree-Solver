using System.Collections.Generic;
public class State
{
  private int value;
  public int Value
  {
      get { return value; }
      set { value = Value; }
  }

  private List<int> domain;
  public List<int> Domain
  {
      get { return domain; }
      set { domain = value; }
  }

  private List<State> peers = new List<State>();
  public List<State> Peers
  {
      get { return peers; }
      set { peers = value; }
  }

  private int id;
  public int Id
  {
      get { return id; }
      set { id = value; }
  }

  public State(int _id)
  {
      id = _id;
  }

  private bool preassigned;
  public bool Preassigned
  {
      get { return preassigned; }
      set { preassigned = value; }
  }
  
  
  
  
  
}