using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using Microsoft.Kinect;
using Microsoft.Kinect.Tools;
using System.Threading;
using System.Windows.Forms;

namespace DepthExtraction
{
    class DepthFrameExtractor
    {
        private int depthFrameWidth = 512;
        private int depthFrameHeight = 424;
        List<ushort[]> depthframes = new List<ushort[]>();

        [STAThread]
        static void Main(string[] args)
        {
            string folder = ChooseFolder();
            //string folder = "d:/kinect-playground";
            string[] xeffilePaths = Directory.GetFiles(folder, "*.xef", SearchOption.AllDirectories);
            System.Console.WriteLine("Files found: " + xeffilePaths.Length.ToString());

            var extractor = new DepthFrameExtractor();
            ParameterizedThreadStart childref = new ParameterizedThreadStart(Play);

            foreach (string xeffilePath in xeffilePaths)
            {
                string depthframePath = xeffilePath.Replace(".xef", "-depthframes.dat");

                Console.WriteLine("Sending " + xeffilePath + " to sensor...");
                Thread childThread = new Thread(childref);
                childThread.Start(xeffilePath);
                while (childThread.IsAlive)
                {
                    Thread.Sleep(500);
                }
                Console.WriteLine("Writing depthframes to " + depthframePath);
                extractor.Process_Depthframes(depthframePath);
                Console.WriteLine("Processing done. Depthframe count: " + extractor.depthframes.LongCount());
                extractor.depthframes.Clear();
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

        public DepthFrameExtractor()
        {
            var sensor = KinectSensor.GetDefault();
            sensor.Open();
            var depthFrameReader = sensor.DepthFrameSource.OpenReader();
            depthFrameReader.FrameArrived += this.Reader_FrameArrived;
        }

        public void Reader_FrameArrived(object sender, DepthFrameArrivedEventArgs e)
        {
            using (DepthFrame depthFrame = e.FrameReference.AcquireFrame())
            {
                if (depthFrame != null)
                {
                    ushort[] depthData = new ushort[depthFrameWidth * depthFrameHeight];
                    depthFrame.CopyFrameDataToArray(depthData);
                    depthframes.Add(depthData);
                }
            }
        }

        public void Process_Depthframes(string depthFramePath)
        {
            using (var depthWriter = new BinaryWriter(File.OpenWrite(depthFramePath)))
            {
                foreach (ushort[] depthFrame in this.depthframes)
                {
                    foreach (ushort u in depthFrame)
                    {
                        depthWriter.Write(BitConverter.GetBytes(u));
                    }
                    depthWriter.Flush();
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