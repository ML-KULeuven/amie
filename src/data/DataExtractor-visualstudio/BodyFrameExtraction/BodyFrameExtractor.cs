using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Kinect;
using Microsoft.Kinect.Tools;
using System.Threading;
using Newtonsoft.Json;
using System.Windows.Forms;

namespace readXEF
{
    class BodyFrameExtractor
    {
        
        List<Body> bodies = new List<Body>();

        [STAThread]
        static void Main(string[] args)
        {

            string folder = ChooseFolder();
            string[] xeffilePaths = Directory.GetFiles(folder, "*.xef", SearchOption.AllDirectories);
            System.Console.WriteLine("Files found: " + xeffilePaths.Length.ToString());

            var extractor = new BodyFrameExtractor();
            ParameterizedThreadStart childref = new ParameterizedThreadStart(Play);
            
            foreach (string xeffilePath in xeffilePaths)
            {
                Console.WriteLine("Sending " + xeffilePath + " to sensor...");

                Thread childThread = new Thread(childref);
                childThread.Start(xeffilePath);
                while (childThread.IsAlive)
                {
                    Thread.Sleep(500);
                }
                string bodyframePath = xeffilePath.Replace(".xef", "-bodyframes.json");
                Console.WriteLine("Writing bodyframe to " + bodyframePath);
                extractor.Process_Bodies(bodyframePath);
                Console.WriteLine("Processing done. Bodycount: " + extractor.bodies.LongCount());
                extractor.bodies.Clear();
            }
            Console.WriteLine("Processed " + xeffilePaths.LongCount() + " .xef files");
        }


        public static string ChooseFolder()
        {
            using (var fbd = new FolderBrowserDialog())
            {
                DialogResult result = fbd.ShowDialog();
                return fbd.SelectedPath;
            }
        }

        public BodyFrameExtractor()
        {
            var sensor = KinectSensor.GetDefault();
            sensor.Open();
            var bodyFrameReader = sensor.BodyFrameSource.OpenReader();
            bodyFrameReader.FrameArrived += this.Reader_FrameArrived;
        }

        private void Process_Bodies(string filePath)
        {
            string kinectBodyDataString = JsonConvert.SerializeObject(this.bodies);
            File.WriteAllText(filePath, kinectBodyDataString);
        }

        private void Reader_FrameArrived(object sender, BodyFrameArrivedEventArgs e)
        {
            using (BodyFrame frame = e.FrameReference.AcquireFrame())
            {
                var bodyAdded = false;
                if (frame != null)
                {
                    var bodies = new Body[frame.BodyCount];
                    // The first time GetAndRefreshBodyData is called, Kinect will allocate each Body in the array.
                    // As long as those body objects are not disposed and not set to null in the array,
                    // those body objects will be re-used.
                    frame.GetAndRefreshBodyData(bodies);
                    var trackedBodies = bodies.Where(b => b.IsTracked == true).ToList();
                    if (trackedBodies.LongCount() >= 1)
                    {
                        this.bodies.Add(trackedBodies.First());
                        bodyAdded = true;
                    }
                }
                if (!bodyAdded)
                {
                    this.bodies.Add(null);
                } 
            }
        }

        public static void Play(object filePathObj)
        {
            using (var client = KStudio.CreateClient())
            {
                string filePath = (string)filePathObj;
                //Console.WriteLine("Connecting to a service");
                client.ConnectToService();
                KStudioEventStreamSelectorCollection streamCollection = new KStudioEventStreamSelectorCollection();
                streamCollection.Add(KStudioEventStreamDataTypeIds.Body);
                using (var playback = client.CreatePlayback(filePath))
                {
                    //Console.WriteLine("Playback created");
                    playback.EndBehavior = KStudioPlaybackEndBehavior.Stop;
                    playback.Start();

                    //for (var j = 0; j < 700; j++)
                    //{
                    //    playback.StepOnce();
                    //    Thread.Sleep(500);
                    //}
                    while (playback.State == KStudioPlaybackState.Playing)
                    {
                        Thread.Sleep(500);
                    }

                    if (playback.State == KStudioPlaybackState.Error)
                    {
                        throw new InvalidOperationException("Error: Playback failed!");
                    }
                }
                //return true;
                //Console.WriteLine("Disconnecting");
                client.DisconnectFromService();
            }
        }
    }
}
