import java.io.*;
import java.util.*;
public class Modif
{ 
	public Modif(){}
	public void print(String s)
	{
		System.out.println(s);
	}
	public static void write_modif(ArrayList<String> to_add) // Ecrit ce qu'il y a à modifier dans un fichier letter_to_add
	{
		try
		{	
			BufferedWriter out = new BufferedWriter(new FileWriter("letter_to_add"));
			
			for(int i=0;i<to_add.size();i++)
			{
			
				out.write(to_add.get(i).toString());
				//print(to_add.get(i).get(j).toString());
				
				out.write("\n");
			}		
			out.close();
		}
		catch(Exception e)
		{
			System.out.println("erreur write_modif");
		}		

	}

	public static ArrayList<String> check_modif(ArrayList<String> orig, ArrayList<String> modif) // Algo qui trouve ce qu'il faut ajouter à la BDD
	{
		int index = 0;
		ArrayList<String> to_add = new ArrayList<String>();
		for(int i=0;i<orig.size();i++)
		{
			//to_add.add(new ArrayList<String>());
			if(i < modif.size())
			{
				for(int j=0;j<orig.get(i).length();j++)
				{

					if((j < modif.get(i).length()) &&(orig.get(i).charAt(j)!=modif.get(i).charAt(j)))
					{
						to_add.add(String.valueOf(j));
						break;
					}
					if(j ==orig.get(i).length() -1)
					{
						to_add.add(String.valueOf(j));
					}
				}

			}
			
			index++;
		}

		return to_add;
	}

}