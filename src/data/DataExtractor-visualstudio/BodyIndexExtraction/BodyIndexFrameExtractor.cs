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

namespace BodyIndexExtraction
{
    class BodyIndexFrameExtractor
    {
        private int depthFrameWidth = 512;
        private int depthFrameHeight = 424;
        List<byte[]> bodyindexframes = new List<byte[]>();

        [STAThread]
        static void Main(string[] args)
        {
            string folder = ChooseFolder();
            //string folder = "d:/kinect-playground";
            string[] xeffilePaths = Directory.GetFiles(folder, "*.xef", SearchOption.AllDirectories);
            System.Console.WriteLine("Files found: " + xeffilePaths.Length.ToString());

            var extractor = new BodyIndexFrameExtractor();
            ParameterizedThreadStart childref = new ParameterizedThreadStart(Play);

            foreach (string xeffilePath in xeffilePaths)
            {
                string bodyindexframePath = xeffilePath.Replace(".xef", "-bodyindexframes.dat");

                Console.WriteLine("Sending " + xeffilePath + " to sensor...");
                Thread childThread = new Thread(childref);
                childThread.Start(xeffilePath);
                while (childThread.IsAlive)
                {
                    Thread.Sleep(500);
                }
                Console.WriteLine("Writing bodyindexframes to " + bodyindexframePath);
                extractor.Process_Bodyindexframes(bodyindexframePath);
                Console.WriteLine("Processing done. Bodyindexframe count: " + extractor.bodyindexframes.LongCount());
                extractor.bodyindexframes.Clear();
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

        public BodyIndexFrameExtractor()
        {
            var sensor = KinectSensor.GetDefault();
            sensor.Open();
            var bodyIndexFrameReader = sensor.BodyIndexFrameSource.OpenReader();
            bodyIndexFrameReader.FrameArrived += this.Reader_FrameArrived;
        }

        public void Reader_FrameArrived(object sender, BodyIndexFrameArrivedEventArgs e)
        {
            using (BodyIndexFrame bodyindexFrame = e.FrameReference.AcquireFrame())
            {
                if (bodyindexFrame != null)
                {
                    byte[] bodyindexData = new byte[depthFrameWidth * depthFrameHeight];
                    bodyindexFrame.CopyFrameDataToArray(bodyindexData);
                    bodyindexframes.Add(bodyindexData);
                }
            }
        }

        public void Process_Bodyindexframes(string bodyindexFramePath)
        {
            using (var bodyindexWriter = new BinaryWriter(File.OpenWrite(bodyindexFramePath)))
            {
                foreach (byte[] bodyindexFrame in this.bodyindexframes)
                {
                    bodyindexWriter.Write(bodyindexFrame);
                    bodyindexWriter.Flush();
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