using System.Collections.Generic;
using System;
using System.Linq;
public class Board
{
  private List<State> _states;
  public List<State> States
  {
      get { return _states; }
      set { _states = value; }
  }
  
  private int _width, _height;
  private int _nodesCount;
  public int NodesCount
  {
    get { return _nodesCount; }
    set { _nodesCount = value; }
  }



  public Board(int width, int height, int n_domain)
  {
    // initialize the board
    _nodesCount = 0;
    _width = width;
    _height = height;
    CreateStates(n_domain);
    ConnectStates();

  }

  public void CreateStates(int n_domain)
  {
    _states = new List<State>();
    List<int> domain = new List<int>();
    for (var i = 1; i <= n_domain; i++)
      domain.Add(i);
    for (var i = 0; i < _width * _height; i++)
      _states.Add(new State(i, domain));
  }

  public void ConnectStates()
  {
    // connect the states
    int row = 0, col = 0;
    for (var i = 0; i < _width * _height; i++)
    {
      col = i % _width;
      row = i / _height;

      if (col - 1 >= 0) _states[i].Peers.Add(_states[i - 1]); //left
      if (col + 1 < _width) _states[i].Peers.Add(_states[i + 1]); //right
      if (row - 1 >= 0) _states[i].Peers.Add(_states[i - _height]); //up
      if (row + 1 < _height) _states[i].Peers.Add(_states[i + _height]); //down

    }
  }

  public void Preassign(Dictionary<int, int> preassignedStates)
  {
    foreach (var stateValue in preassignedStates)
    {
      _states[stateValue.Key].Value = stateValue.Value;
      _states[stateValue.Key].Preassigned = true;
      _states[stateValue.Key].Active = true;
    }
    // PrintBoard();
  }

  public bool IsAssigned()
  {
    foreach (var state in _states) if (state.Value == -1) return false;

    return true;
  }

  public List<State> UnassignedStates()
  {
    List<State> temp = new List<State>();
    foreach (var state in _states)
    {
      if (state.Value == -1) temp.Add(state);
    }
    return temp;
  }

  public List<State> GetActiveStates()
  {
    List<State> temp = new List<State>();
    foreach (var state in _states)
    {
      if(state.Active) temp.Add(state);
    }
    return temp;
  }
  
  // this orders the list based on the number of peers (ascending) -- so, MRV?
  public List<State> GetActiveStatesOrdered()
  {
    List<State> temp = GetActiveStates().OrderBy(o=>o.GetUnassignedPeers().Count).ToList();
    // List<State> temp = GetActiveStates().OrderByDescending(o=>o.GetUnassignedPeers().Count).ToList();
    return temp;
  }
  // objListOrder.OrderBy(o=>o.OrderDate).ToList()

  public List<State> AssignedStates()
  {
    List<State> temp = new List<State>();
    foreach (var state in _states)
    {
      if (state.Value != -1) temp.Add(state);
    }
    return temp;
  }

  public bool IsValid()
  {
    foreach (var state in _states)
    {
      if (!state.IsConstraintsValid()) return false;
    }
    return true;
  }

  public void PrintBoard()
  {
    for (var i = 0; i < _height; i++)
    {
      for (var j = 0; j < _width; j++)
      {
        Console.Write(_states[i * _height + j].Value + "\t");
      }
      Console.WriteLine("");
    }
  }

  public string GetBoardString()
  {
    string str = "";
    foreach (var state in _states)
    {
      if(state.Value == -1) str += "x";
      else str += state.Value.ToString();
    }
    return str;
  }

}