package openscope;

import java.awt.Component;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
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
	public Thread mainThread = null;
	DataInputStream dis;
	Component parent;
	HttpsURLConnection conn = null;
	private Image image = null, im = null;
	public Dimension imageSize = null;

	public MicroCam(Component parent_) {
		parent = parent_;
	}

	public void connect() throws Exception {
		URL url = new URL("https://" + Start_Connection.ip
				+ ":9000/_stream/?action=stream");
		// URL url = new URL("http://131.111.125.248/axis-cgi/mjpg/video.cgi");
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

		BufferedInputStream bis = new BufferedInputStream(is);
		dis = new DataInputStream(bis);
		readStream();
		initDisplay();
	}

	public void initDisplay() {
		imageSize = new Dimension(image.getWidth(this), image.getHeight(this));
		setPreferredSize(imageSize);
		parent.setSize(imageSize);
		parent.validate();
	}

	public void readStream() throws Exception {
		String line = "";
		int len = 0;

		while (!(line = dis.readLine().trim()).equals("")) {
			// System.out.println(line);
			if (line.startsWith("Content-Length"))
				len = Integer.parseInt(line.split(" ")[1]);
		}

		byte[] bb = new byte[len];
		dis.readFully(bb, 0, len);

		ByteArrayInputStream bbi = new ByteArrayInputStream(bb);
		if ((im = ImageIO.read(bbi)) != null)
			image = im;
		bbi.close();
	}

	public void paint(Graphics g) {
		if (image != null)
			g.drawImage(image, 0, 0, this);
	}

	public void run() {
		try {
			connect();
			while (true) {
				readStream();
				parent.repaint();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static JFrame launch() {
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
		return main;
	}
}
