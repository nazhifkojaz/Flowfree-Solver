using System.Collections.Generic;
using System;
public class Board
{
  private List<State> _states = new List<State>();
  private int _width, _height;
  
  
  public Board(int width, int height, List<int> domain)
  {
    // initialize the board
    _width = width;
    _height = height;
      for (var i = 0; i < width * height; i++)
        _states.Add(new State(i, domain));
    // connect the states
    int row =0, col = 0;
    for (var i = 0; i < width * height; i++)
    {
      col = i % width;
      row = i / height;

      if(col-1 >= 0) _states[i].Peers.Add(_states[i-1]); //left
      if(col+1 < width) _states[i].Peers.Add(_states[i+1]); //right
      if(row-1 >= 0) _states[i].Peers.Add(_states[i-height]); //up
      if(row+1 < height) _states[i].Peers.Add(_states[i+height]); //down

    }
  }

  public void Preassign(Dictionary<int, int> preassignedStates)
  {
    foreach (var stateValue in preassignedStates)
    {
      _states[stateValue.Key].Value = stateValue.Value;
      _states[stateValue.Key].Preassigned = true;
    }
  }

  public bool IsAssigned()
  {
    foreach (var state in _states) if(state.Value == -1) return false;
    
    return true;
  }

  public List<State> UnassignedStates()
  {
    List<State> temp = new List<State>();
    foreach (var state in _states)
    {
      if(state.Value == -1) temp.Add(state);
    }
    return temp;
  }

  public bool IsValid()
  {
    foreach (var state in _states)
    {
      if(!state.IsConstraintsValid()) return false;
    }
    return true;
  }

  public void PrintBoard()
  {
    for (var i = 0; i < _height; i++)
    {
      for (var j = 0; j < _width; j++)
      {
        Console.Write(_states[i*_height + j].Value + "\t");
      }
      Console.WriteLine("");
    }
  }
  
}