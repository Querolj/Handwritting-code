import java.io.*;
import java.util.*;
public class main
{ 

	public static void main(String [] args)
	{
		Modif modif = new Modif();
		ArrayList<String> test = new ArrayList<String>();
		ArrayList<String> mod = new ArrayList<String>();
		System.out.println(args);
		test.add("123456789123456789123456789123456789");
		test.add("123456aed");
		mod.add("1234567891234567891234567kopjpo89123456789");
		mod.add("fghjklghjklyuio");

		ArrayList<String> res = modif.check_modif(test, mod);
		System.out.println(res);
		for(int i=0;i<args.lenght();i++)
		{
			System.out.println(args[i]);
		}
		modif.write_modif(res);
	}


}