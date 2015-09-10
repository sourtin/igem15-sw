package openscope;

import java.awt.Component;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;

import javax.imageio.ImageIO;
import javax.net.ssl.HttpsURLConnection;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPanel;

public class MicroCam extends JPanel implements Runnable {
	DataInputStream dis;
	private Image image = null;
	public Dimension imageSize = null;
	public boolean connected = false;
	private boolean initCompleted = false;
	HttpsURLConnection conn = null;
	Component parent;

	public MicroCam(Component parent_) {
		parent = parent_;
	}

	public void connect() {
		try {
			
			
			URL url = new URL("https://"+Start_Connection.ip+":9000/_stream/?action=stream");
			conn = (HttpsURLConnection) url.openConnection();

			if (conn.getResponseCode() == 401) {
				// incorrect username password combo
				JOptionPane
						.showMessageDialog(
								null,
								"Incorrect username/password combo... Could not authenticate, but managed to connect.");
				conn.disconnect();
				return;
			}

			BufferedReader in = new BufferedReader(new InputStreamReader(
					conn.getInputStream()));
			InputStream is = conn.getInputStream();
			connected = true;
			BufferedInputStream bis = new BufferedInputStream(is);
			dis = new DataInputStream(bis);
			readMJPGStream();
			if (!initCompleted)
				initDisplay();

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public void initDisplay() {

		imageSize = new Dimension(image.getWidth(this), image.getHeight(this));
		setPreferredSize(imageSize);
		parent.setSize(imageSize);
		parent.validate();
		initCompleted = true;
	}

	long len = 0;

	public void readMJPGStream() {
		readLine(5, dis, "\n");
		readJPG();
		readLine(1, dis, "--boundary");
	}

	public void readLine(int n, DataInputStream dis, String lineEnd) {
		for (int i = 0; i < n; i++) {
			try {
				byte[] lineEndBytes = lineEnd.getBytes();
				byte[] byteBuf = new byte[lineEndBytes.length];
				boolean end = false;

				while (!end) {
					dis.read(byteBuf, 0, lineEndBytes.length);
					String t = new String(byteBuf);

					//System.out.print(t);
					if (t.equals(lineEnd))
						end = true;
				}
			} catch (Exception e) {
				e.printStackTrace();
			}

		}
	}

	public void disconnect() {
		try {
			if (connected) {
				dis.close();
				conn.disconnect();
				connected = false;
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public void paint(Graphics g) {
		if (image != null)
			g.drawImage(image, 0, 0, this);
	}

	public void readJPG() {
		try {
			image = ImageIO.read(dis);
			//System.out.println("read image: " + image);
		} catch (Exception e) {
			e.printStackTrace();
			disconnect();
		}
	}

	public void run() {
		connect();
		try {
			while (true) {
				readMJPGStream();
				parent.repaint();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public Thread mainThread = null;

	public static void launch() {
		final JFrame main = new JFrame("Live view");
		
		final MicroCam panel = new MicroCam(main);
		panel.mainThread = new Thread(panel);
		panel.mainThread.start();
		
		main.getContentPane().add(panel);
		WindowAdapter wa = new WindowAdapter() {
	        // WINDOW_CLOSING event handler
	        @Override
	        public void windowClosing(WindowEvent e) {
	            super.windowClosing(e);
	            panel.mainThread.stop();
	        }

	        @Override
	        public void windowClosed(WindowEvent e) {
	            super.windowClosed(e);
	        }
	    };

	    main.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
	    main.addWindowListener(wa);
	    
		main.pack();
		main.show();
	}
}
