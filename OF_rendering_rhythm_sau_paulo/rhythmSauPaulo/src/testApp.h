#pragma once

#include "ofMain.h"
#include "ofxSVG.h"
#include "ofxUI.h"
#include "ofxOsc.h"
#include "ofxParticleSystem.h"

// listen on port 12345
#define PORT 12345

class testApp : public ofBaseApp{
	public:
		void setup();
		void update();
		void draw();
		
		void keyPressed(int key);
		void keyReleased(int key);
		void mouseMoved(int x, int y);
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);
        void exit();
        //
        void drawPatternSVG(ofxSVG * svg, ofColor c);
        void simulation2D();
        void guiEvent(ofxUIEventArgs &e);
        void setupGUI();
        void drawMetronomStick(ofFbo *_fbo,float extraTheta=0,float x=0,float y=0);
        void drawInfo();
        void drawMask(ofFbo *_fbo,ofImage *_mask, int x, int y);
        void drawEffectDataUpdate();
        //
        ofFbo fbo;
        ofFbo fboRight;
        ofFbo fboLeft;
    
        ofFbo fboEffects;
        ofVec3f vertexCoordinates[12];
        ofVec3f textureCoordinates[12];
        ofVec3f points[8];

        float theta;
        int lastIncrement;
        int direction;
        float stickWidth;
        float stickHeight;
        float velocity;
        float velocityMin;
        float minTheta;
        float maxTheta;
        float trX;
        float trY;
    
        int nextCityRhythm;
        int cityRhythm;
        int cityRhythm_rawTwitter;
        int cityRhythm_Twitter;
        int cityRhythm_rawFlickr;
        int cityRhythm_Flickr;
        int cityRhythm_rawYoutube;
        int cityRhythm_Youtube; 
        int counterOSCMessages;
    
        
        ofxSVG* svgLeft;
        ofxSVG* svgCenter;
        ofxSVG* svgRight;
        ofxSVG* svgLines;
        ofxSVG* svgDetails;
        
        ofxUICanvas *gui;   	
        ofxOscReceiver receiver;
        

        ofColor color1; 
        ofColor color2; 
        ofColor color3; 
        unsigned long long timeLastMove;
        unsigned long long timeLastDirection;
        unsigned long long timeLastDataUpdate;
    
        ofxParticleSystem particleSystem;
        ofShader maskShader;
        ofImage maskCenter;
        ofImage maskAll;
        ofImage maskLeft;
        ofImage maskRight;
        bool guiVisible;
        bool showLines;
        bool fullscreen;
        bool testColors;
    
        
};
