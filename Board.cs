using System.Collections.Generic;
public class Board
{
  private List<State> _states = new List<State>();
  
  
  public Board(int width, int height, List<int> domain)
  {
    // initialize the board
      for (var i = 0; i < width * height; i++)
        _states.Add(new State(i));
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

    // pre-assign the board
    _states[0].Value = 1;
    _states[7].Value = 1;
    _states[4].Value = 2;
    _states[6].Value = 2;
    
    // solve the board

  }
  
}