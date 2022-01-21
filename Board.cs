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
  private Random _rand;
  
  private int _colors;
  public int Colors
  {
      get { return _colors; }
      set { _colors = value; }
  }
  
  private int[] _colorCounter;
  public int[] ColorCounter
  {
      get { return _colorCounter; }
      set { _colorCounter = value; }
  }
  
  
  public int Width
  {
    get { return _width;}
  }
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
    _colors = n_domain;
    _width = width;
    _height = height;
    CreateStates(n_domain);
    ConnectStates();
  }
  public Board(int width, int n_colors)
  {
    _nodesCount = 0;
    _colors = n_colors;
    _width = width;
    _height = width;
    CreateStates();
    ConnectStates();
    _rand = new Random();
    Populate(n_colors);
    PrintBoard();
  }
  public Board(int width, int n_colors, String initial)
  {
      _nodesCount = 0;
      _colors = n_colors;
      _width = width;
      _height = width;
      CreateStates();
      ConnectStates();
      _rand = new Random();
      AssignInitial(initial);
      PrintBoard();
  }
  
  public void Populate(int n_colors)
  { //as its name, this method is to populate the board with random colors
    _colorCounter = new int[n_colors];
    // put 3 for each color
    // put the heads / preassigned state, randomly of course
    for (int i = 0; i < n_colors; i++)
    {
      int idx;
      do
      { // to make sure it's empty
          idx = _rand.Next(_height*_width);
      } while (_states[idx].Value != -1);
      
      _states[idx].Value = i;
      // _states[idx].Preassigned = true;
      
      _colorCounter[i] = 1;
    }
    foreach (var state in UnassignedStates())
    {
        if(notEnough() != -1)
        {
          state.Value = notEnough();
          _colorCounter[state.Value]++;
        } 
        else if(notEnough() == -1)
        {
          state.Value = _rand.Next(n_colors);
          _colorCounter[state.Value]++;
        }
    }
    
  }
  
  int notEnough()
  {
    for (int i = 0; i < _colorCounter.Length; i++)
        if(ColorCounter[i] < 3) return i;
    return -1;
  }
  
  public int GetEmptyIndex()
  {
    int idx;
    do
    {
        idx = _rand.Next(_height*_width);
    } while (_states[idx].Value != -1);
    return idx;
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
  public void CreateStates()
  {
    _states = new List<State>();
    for (int i = 0; i < _width * _height; i++)
      _states.Add(new State(i));
  }

  public void ConnectStates()
  {
    // connect the states
    int row = 0, col = 0;
    for (var i = 0; i < _width * _height; i++)
    {
      col = i % _width;
      row = i / _height;

      if (col - 1 >= 0)
      {
        _states[i].Peers.Add(_states[i - 1]); //left
        _states[i].Left = i-1;
      } else {_states[i].Left = -1;}
      if (col + 1 < _width)
      {
        _states[i].Peers.Add(_states[i + 1]); //right
        _states[i].Right = i+1;
      } else {_states[i].Right = -1;}
      if (row - 1 >= 0)
      {
        _states[i].Peers.Add(_states[i - _height]); //up
        _states[i].Top = i-_height;
      } else {_states[i].Top = -1;}
      if (row + 1 < _height)
      {
        _states[i].Peers.Add(_states[i + _height]); //down
        _states[i].Bot = i+_height;
      } else {_states[i].Bot = -1;}
    }
  }
  
  public void AssignInitial(String initial)
  {
    for (int i = 0; i < initial.Length; i++)
    {
      if(initial[i] == 'x') _states[i].Value = -1;
      else
      {
        _states[i].Active = true;
        _states[i].Value = Convert.ToInt32(Char.GetNumericValue(initial[i]));
      }
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
  public bool isActivated()
  {
    foreach (var state in _states) if(!state.Active) return false;
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
      if (state.Active) temp.Add(state);
    }
    return temp;
  }
  
  public List<State> GetInactiveStates()
  {
    List<State> temp = new List<State>();
    foreach (var state in _states)
      if(!state.Active) temp.Add(state); 
    return temp;
  }
  public List<State> GetInactiveStatesByColor(int col, int id)
  {
    List<State> temp = new List<State>();
    foreach (var state in _states)
    {
        if(!state.Active && state.Value == col && state.Id != id) temp.Add(state);
    }
    return temp;
  }
  public List<State> GetInactiveStatesOrdered()
  {
    return GetInactiveStates().OrderBy(o => o.Value).ToList();
  }
  
  public List<State> GetPreassignedStates()
  {
    List<State> temp = new List<State>();
    foreach (var state in _states)
    {
        if(state.Preassigned && !state.Active) temp.Add(state);
    }
    return temp.OrderBy(o => o.Value).ToList();
  }

  // this orders the list based on the number of peers (ascending) -- so, MRV?
  public List<State> GetActiveStatesOrdered()
  {
    List<State> temp = GetActiveStates().OrderBy(o => o.GetUnassignedPeers().Count).ToList();
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
      if (state.Value == -1) str += "x";
      else str += state.Value.ToString();
    }
    return str;
  }

  public int GetNumberOfLines()
  {
    int lines = 0;
    foreach (var state in _states)
    {
      bool isEdge = false;
      if(state.Top != -1 && _states[state.Top].Value == state.Value)
      {
        if(state.Left != -1 && _states[state.Left].Value == state.Value) isEdge = true;
        if(state.Right != -1 && _states[state.Right].Value == state.Value) isEdge = true;
      } else if(state.Bot != -1 && _states[state.Bot].Value == state.Value)
      {
        if(state.Left != -1 && _states[state.Left].Value == state.Value) isEdge = true;
        if(state.Right != -1 && _states[state.Right].Value == state.Value) isEdge = true;
      }
      // if(((_states[state.Top].Value == state.Value) || (_states[state.Bot].Value == state.Value)) && ((_states[state.Left].Value == state.Value) || (_states[state.Right].Value == state.Value))) isEdge = true;
     // if(state.Bot != -1 && (state.Left == -1 || state.Right == -1))
        // if(_states[state.Bot].Value == state.Value && (_states[state.Left].Value == state.Value || _states[state.Right].Value == state.Value)) isEdge = true;
      if (isEdge) lines++;
    }
    return lines + _colors;
  }
  
  public int GetColorPair(int id, int color)
  {
    int goal = id;
    foreach (var state in GetActiveStates())
        if(state.Id != goal && state.Value == color) goal = state.Id;
    return goal;
  }

}