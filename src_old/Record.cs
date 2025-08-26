using System.Collections.Generic;
public class Record
{
  public int Value;
  public List<State> AffectedPeers;
  public Record(int value, List<State> affectedPeers)
  {
      Value = value;
      AffectedPeers = affectedPeers;
  }
}