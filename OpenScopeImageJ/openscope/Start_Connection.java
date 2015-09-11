package openscope;

import ij.IJ;
import ij.plugin.PlugIn;

import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.Authenticator;
import java.net.ConnectException;
import java.net.InetAddress;
import java.net.PasswordAuthentication;
import java.net.URL;
import java.net.UnknownHostException;
import java.security.SecureRandom;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.KeyManager;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextField;

public class Start_Connection implements PlugIn, KeyListener {

	HostnameVerifier ignore = null;
	public static String ip = "172.29.9.20";
	public static String user = "admin", pass = "test";

	public static JFrame mainWindow = null;

	JTextField motor0, motor1, motor2;

	@Override
	public void run(String arg) {
		try {
			Connection_Settings.loadSettings();

			if (!InetAddress.getByName(ip).isReachable(1000))
				throw (new ConnectException());

			SSLContext ctx = SSLContext.getInstance("TLS");
			ctx.init(new KeyManager[0],
					new TrustManager[] { new DefaultTrustManager() },
					new SecureRandom());
			SSLContext.setDefault(ctx);

			HttpsURLConnection
					.setDefaultHostnameVerifier(new HostnameVerifier() {
						public boolean verify(String hostname,
								SSLSession session) {
							return true;
						}
					});

			Authenticator.setDefault(new Authenticator() {
				protected PasswordAuthentication getPasswordAuthentication() {
					return new PasswordAuthentication(user, pass.toCharArray());
				}
			});

		} catch (ConnectException e) {
			JOptionPane.showMessageDialog(null,
					"Could not connect to openscope - incorrect ip?");
			e.printStackTrace();
		} catch (UnknownHostException e) {
			JOptionPane.showMessageDialog(null,
					"Invalid hostname - could not connect to openscope.");
			e.printStackTrace();
		} catch (IOException e) {
			JOptionPane.showMessageDialog(null,
					"IO exception while trying to connect to openscope...");
			e.printStackTrace();
		} catch (Exception e) {
			JOptionPane.showMessageDialog(null, "Exotic error...");
			e.printStackTrace();
		}

		// show swing ui
		if (mainWindow == null) {
			mainWindow = new JFrame("OpenScope control");
			JPanel panel = new JPanel();
			// mainWindow.addKeyListener(this);

			panel.setPreferredSize(new Dimension(450, 160));

			JButton capture = new JButton("Capture image");
			capture.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					captureAndOpen();
				}
			});
			panel.add(capture);
			JButton toggle = new JButton("Toggle LEDs");
			toggle.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					toggleLed();
				}
			});
			panel.add(toggle);
			JButton live = new JButton("Show Live View");
			live.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {

					try {
						// Desktop.getDesktop().browse(URI.create("https://"+ip+":9000/force_ministream.html"));
						MicroCam.launch().addKeyListener(Start_Connection.this);
					} catch (Exception e) {
						e.printStackTrace();
					}
				}
			});
			panel.add(live);

			JLabel label = new JLabel("X step: ");
			motor0 = new JTextField("100");
			motor0.setPreferredSize(new Dimension(220, 20));
			panel.add(label);
			panel.add(motor0);

			JButton go0 = new JButton("Go");
			go0.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					move(0, Integer.parseInt(motor0.getText()));
				}
			});
			panel.add(go0);
			JButton go0b = new JButton("Back");
			go0b.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					move(0, -1 * Integer.parseInt(motor0.getText()));
				}
			});
			panel.add(go0b);

			JLabel label2 = new JLabel("Y step: ");
			motor1 = new JTextField("100");
			motor1.setPreferredSize(new Dimension(220, 20));
			panel.add(label2);
			panel.add(motor1);

			JButton go1 = new JButton("Go");
			go1.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					move(1, Integer.parseInt(motor1.getText()));
				}
			});
			panel.add(go1);
			JButton go1b = new JButton("Back");
			go1b.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					move(1, -1 * Integer.parseInt(motor1.getText()));
				}
			});
			panel.add(go1b);
			JLabel label3 = new JLabel("Z step: ");
			motor2 = new JTextField("600");
			motor2.setPreferredSize(new Dimension(220, 20));
			panel.add(label3);
			panel.add(motor2);

			JButton go2 = new JButton("Go");
			go2.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					move(2, Integer.parseInt(motor2.getText()));
				}
			});
			panel.add(go2);

			JButton go2b = new JButton("Back");
			go2b.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					move(2, -1 * Integer.parseInt(motor2.getText()));
				}
			});
			panel.add(go2b);

			JButton bf = new JButton("Brightfield");
			bf.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					setLed(0);
				}
			});
			panel.add(bf);
			JButton fl = new JButton("Fluorescence");
			fl.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					setLed(1);
				}
			});
			panel.add(fl);
			JButton off = new JButton("Off");
			off.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent ae) {
					setLed(2);
				}
			});
			panel.add(off);

			mainWindow.setFocusTraversalKeysEnabled(false);
			capture.addKeyListener(this);
			toggle.addKeyListener(this);
			live.addKeyListener(this);
			go0.addKeyListener(this);
			go0b.addKeyListener(this);
			go1.addKeyListener(this);
			go1b.addKeyListener(this);
			go2.addKeyListener(this);
			go2b.addKeyListener(this);

			bf.addKeyListener(this);
			fl.addKeyListener(this);
			off.addKeyListener(this);
			mainWindow.getContentPane().add(panel);
			mainWindow.pack();
		}

		mainWindow.setVisible(true);
		// MicroCam.launch();
	}

	public static void captureAndOpen() {
		try { // im lazy, okay?
			URL url = new URL("https://" + ip + ":9000/_webshell/capture/");
			HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();

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
			String location;
			location = in.readLine();
			System.out.println(location);
			in.close();
			conn.disconnect();

			url = new URL("https://" + ip + ":9000" + location);
			conn = (HttpsURLConnection) url.openConnection();

			InputStream inputStream = conn.getInputStream();

			FileOutputStream outputStream = new FileOutputStream(new File(
					System.getProperty("java.io.tmpdir") + File.separator
							+ "captured.png"));

			int read = 0;
			byte[] bytes = new byte[1024];

			while ((read = inputStream.read(bytes)) != -1) {
				outputStream.write(bytes, 0, read);
			}

			outputStream.close();
			inputStream.close();
			conn.disconnect();

			IJ.open(System.getProperty("java.io.tmpdir") + File.separator
					+ "captured.png");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void move(int axis, int amount) {
		try {
			URL url = new URL("https://" + ip
					+ ":9000/_webshell/control/motor/" + axis + "/" + amount);
			HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();

			if (conn.getResponseCode() == 401) {
				// incorrect username password combo
				JOptionPane
						.showMessageDialog(
								null,
								"Incorrect username/password combo... Could not authenticate, but managed to connect.");
				conn.disconnect();
				return;
			}

			if (conn.getResponseCode() != 200) {
				JOptionPane.showMessageDialog(null,
						"Unknown server side error...");
				conn.disconnect();
				return;
			}

			conn.disconnect();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void setLed(int led) {
		try {

			URL url = new URL("https://" + ip
					+ ":9000/_webshell/control/led/set/" + led);
			HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();

			if (conn.getResponseCode() == 401) {
				// incorrect username password combo
				JOptionPane
						.showMessageDialog(
								null,
								"Incorrect username/password combo... Could not authenticate, but managed to connect.");
				conn.disconnect();
				return;
			}

			if (conn.getResponseCode() != 200) {
				JOptionPane.showMessageDialog(null,
						"Unknown server side error...");
				conn.disconnect();
				return;
			}

			conn.disconnect();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void toggleLed() {
		try {

			URL url = new URL("https://" + ip
					+ ":9000/_webshell/control/led/toggle/_");
			HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();

			if (conn.getResponseCode() == 401) {
				// incorrect username password combo
				JOptionPane
						.showMessageDialog(
								null,
								"Incorrect username/password combo... Could not authenticate, but managed to connect.");
				conn.disconnect();
				return;
			}

			if (conn.getResponseCode() != 200) {
				JOptionPane.showMessageDialog(null,
						"Unknown server side error...");
				conn.disconnect();
				return;
			}

			conn.disconnect();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static class DefaultTrustManager implements X509TrustManager {
		@Override
		public void checkClientTrusted(X509Certificate[] arg0, String arg1)
				throws CertificateException {
		}

		@Override
		public void checkServerTrusted(X509Certificate[] arg0, String arg1)
				throws CertificateException {
		}

		@Override
		public X509Certificate[] getAcceptedIssuers() {
			return null;
		}
	}

	@Override
	public void keyPressed(KeyEvent arg0) {
	}

	@Override
	public void keyReleased(KeyEvent arg0) {
		if (arg0.getKeyCode() == KeyEvent.VK_DOWN) {
			move(1, Integer.parseInt(motor1.getText()));
		} else if (arg0.getKeyCode() == KeyEvent.VK_UP) {
			move(1, -1 * Integer.parseInt(motor1.getText()));
		} else if (arg0.getKeyCode() == KeyEvent.VK_RIGHT) {
			move(0, Integer.parseInt(motor0.getText()));
		} else if (arg0.getKeyCode() == KeyEvent.VK_LEFT) {
			move(0, -1 * Integer.parseInt(motor0.getText()));
		} else if (arg0.getKeyCode() == KeyEvent.VK_SHIFT) {
			toggleLed();
		} else if (arg0.getKeyChar() == 'a') {
			move(2, Integer.parseInt(motor2.getText()));
		} else if (arg0.getKeyChar() == 's') {
			move(2, -1 * Integer.parseInt(motor2.getText()));
		}
	}

	@Override
	public void keyTyped(KeyEvent arg0) {
	}
}
