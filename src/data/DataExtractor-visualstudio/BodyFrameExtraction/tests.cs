using Microsoft.Kinect;
using System;
using Microsoft.Kinect.Tools;
using Microsoft.Win32;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows;

namespace readXEF
{
	class tests
	{
		int i = 0;
		/// <summary>
		/// 
		/// </summary>
		/// <param name="args"></param>
		//static void Main(string[] args)
		//{
		//	//new Program();

  //          tests.Play("D:/kinect/testrun.xef");
		//}
		public tests()
		{
			Console.WriteLine("Hello World using C#!");
			var client = KStudio.CreateClient();
			client.ConnectToService();
			Console.WriteLine("KStudio client created!");
			string filePath = "D:/kinect/testrun.xef";
			Console.WriteLine(File.Exists(filePath) ? "File exists." : "File does not exist.");
			var sensor = KinectSensor.GetDefault();
			var xeffile = client.OpenEventFile(filePath);

			var bodyFrameReader = sensor.BodyFrameSource.OpenReader();
			bodyFrameReader.FrameArrived += this.Reader_FrameArrived;

			

			using (KStudioPlayback playback = client.CreatePlayback(xeffile))
			{
				playback.LoopCount = 1;
				playback.Start();
				Console.WriteLine(sensor.IsAvailable);

				var j = 0;
				//playback.
				while (playback.State == KStudioPlaybackState.Playing)
				//while( i < 700)
				{
					//playback.
					//Thread.Sleep(50);
					//Console.WriteLine("stuff " + j);
					//playback.StepOnce();
					//j++;
				}

				if (playback.State == KStudioPlaybackState.Error)
				{
					throw new InvalidOperationException("Error: Playback failed!");
				}
			}
			//foreach (var item in xeffile.EventStreams)
			//{
			//	if (item.DataTypeName.Equals("Nui Body Frame"))
			//	{
			//		KStudioSeekableEventStream stream = item as KStudioSeekableEventStream;
			//		var frameCount = (int)stream.EventCount;
			//		var timing = new ushort[frameCount];
			//		Console.WriteLine(frameCount);
			//		var curr_event = stream.ReadEvent(0);
			//		Console.WriteLine(curr_event.ToString());
			//		auto bodies = ref new Platform::Collections::Vector<Body^> (6);
			//		curr_event.
			//	}
			//}

		}

		private void Reader_FrameArrived(object sender, BodyFrameArrivedEventArgs e)
		{
			Console.WriteLine("frame" + i);
			i++;
		}

        public static bool Play(string fileName)
        {
            using (var client = KStudio.CreateClient())
            {
                Console.WriteLine("Connecting to a service");
                client.ConnectToService();
                using (var playback = client.CreatePlayback(fileName))
                {
                    Console.WriteLine("Playback created");
                    playback.EndBehavior = KStudioPlaybackEndBehavior.Stop;
                    playback.Start();
                    while (playback.State == KStudioPlaybackState.Playing)
                    {
                        Thread.Sleep(500);
                    }

                    if (playback.State == KStudioPlaybackState.Error)
                    {
                        throw new InvalidOperationException("Error: Playback failed!");
                    }
                }
                Console.WriteLine("Disconnecting");
                client.DisconnectFromService();
                return true;
            }
        }

    }

}
