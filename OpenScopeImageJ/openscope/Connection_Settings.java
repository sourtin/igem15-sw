package openscope;

import ij.plugin.PlugIn;

import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Properties;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;

public class Connection_Settings implements PlugIn {

	public static JFrame settingsWindow = null;
	public static JTextField ipField = null, userField = null;
	public static JPasswordField passField = null;
	
	public static void loadSettings() {
		Properties properties = new Properties();
		try {
			new File(System.getProperty("user.home")
					+ File.separator + ".ij.openscope.settings").createNewFile();
			properties.load(new FileInputStream(System.getProperty("user.home")
					+ File.separator + ".ij.openscope.settings"));
			Start_Connection.ip = properties.getProperty("ip");
			Start_Connection.user = properties.getProperty("user");
			Start_Connection.pass = properties.getProperty("pass");
		} catch (IOException e) {
			e.printStackTrace();
		}
		if (Start_Connection.ip == null)
			Start_Connection.ip = "raspberrypi.local";
		if (Start_Connection.user == null)
			Start_Connection.user = "admin";
		if (Start_Connection.pass == null)
			Start_Connection.pass = "";
	}

	@Override
	public void run(String arg) {
		// show window
		if (settingsWindow == null) {
			settingsWindow = new JFrame("OpenScope plugin settings");

			JPanel panel = new JPanel();
			
			JLabel label = new JLabel("IP/Hostname: ");
			ipField = new JTextField();
			ipField.setPreferredSize(new Dimension(330, 20));

			JLabel label2 = new JLabel("Username: ");
			userField = new JTextField();
			userField.setPreferredSize(new Dimension(330, 20));

			JLabel label3 = new JLabel("Password: ");
			passField = new JPasswordField();
			passField.setPreferredSize(new Dimension(330, 20));

			JButton doneBtn = new JButton("Done");

			panel.add(label);
			panel.add(ipField);
			panel.add(label2);
			panel.add(userField);
			panel.add(label3);
			panel.add(passField);
			panel.add(doneBtn);

			panel.setPreferredSize(new Dimension(450, 130));
			
			doneBtn.addActionListener(new ActionListener() {
	            public void actionPerformed(ActionEvent ae) {
	            	Properties properties = new Properties();
	        		try {
	        			Start_Connection.ip = ipField.getText();
	        			Start_Connection.user = userField.getText();
	        			Start_Connection.pass = passField.getText();
	        			File f = new File(System.getProperty("user.home")
	        					+ File.separator + ".ij.openscope.settings");
	        			f.createNewFile();
	        			properties.load(new FileInputStream(System.getProperty("user.home")
	        					+ File.separator + ".ij.openscope.settings"));
	        			properties.setProperty("ip", Start_Connection.ip);
	        			properties.setProperty("user", Start_Connection.user);
	        			properties.setProperty("pass", Start_Connection.pass);
	                    OutputStream out = new FileOutputStream( f );
	        			properties.store(out, "");
	        			settingsWindow.setVisible(false);
	        		} catch (IOException e) {
	        			e.printStackTrace();
	        		}
	            }
	        });

			settingsWindow.getContentPane().add(panel);
			settingsWindow.pack();
		}

		loadSettings();

		ipField.setText(Start_Connection.ip);
		userField.setText(Start_Connection.user);
		passField.setText(Start_Connection.pass);

		settingsWindow.setVisible(true);
	}

}
