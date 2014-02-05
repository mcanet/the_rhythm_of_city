#include "testApp.h"

//--------------------------------------------------------------

void testApp::setup(){
    // setup App
    ofSetVerticalSync(true);
    ofSetFrameRate(30);
    
    svgLeft = new ofxSVG();
    svgRight = new ofxSVG();
    svgCenter = new ofxSVG();
    svgLines = new ofxSVG();
    svgDetails = new ofxSVG();
    
    svgDetails->load("detalls.svg");
    svgLeft->load("leftSide.svg");
    svgRight->load("rightSide.svg");
    svgCenter->load("centerSide.svg");
    svgLines->load("lines.svg");
    
    fbo.allocate(300, 200);   
    fbo.setUseTexture(true);
    fboEffects.allocate(300, 200); 
    fboEffects.setUseTexture(true);
    
    fboRight.allocate(300, 200);
    fboRight.setUseTexture(true);
    fboLeft.allocate(300, 200); 
    fboLeft.setUseTexture(true);
    
    maskAll.loadImage("mask/maskAll_invert.png");
    maskCenter.loadImage("mask/mask_invert.png");
    maskLeft.loadImage("mask/maskLeft_invert.png");
	maskRight.loadImage("mask/maskRight_invert.png");
    maskShader.load("mask/composite");
    
    cityRhythm = 0;
    nextCityRhythm = 0;
    stickHeight = 300;
    stickWidth = 2.66; 
    minTheta = 4.0;
    maxTheta = 5.3;
    theta = minTheta;
    velocity = .17;
    velocityMin = .01;
    direction = 1;
    direction = 1;
    color1 = ofColor(0,0,255);
    color2 = ofColor(255,0,0);
    trX = 0;
    trY = -stickHeight;
    setupGUI();
    receiver.setup(PORT);
    timeLastDataUpdate = (ofGetElapsedTimeMillis()-60000);
    testColors = false;
    
    particleSystem = ofxParticleSystem();
    ofSetWindowTitle("Rhythm of Sao Paulo - 2012 (Varvara Guljajeva and Mar Canet)");
}

//--------------------------------------------------------------

void testApp::update(){
    if((ofGetElapsedTimeMillis()-timeLastMove)>50 ){
        theta = theta+(velocityMin+(velocity*(((float)cityRhythm)/255.0f))) * direction;
        timeLastMove = ofGetElapsedTimeMillis();
        
        // progressive change
        if(abs(cityRhythm-nextCityRhythm)<=10) cityRhythm =nextCityRhythm;
        if(cityRhythm < nextCityRhythm) cityRhythm +=10;
        if(cityRhythm > nextCityRhythm) cityRhythm -=10;
        if(cityRhythm <0) cityRhythm =0;
        if(cityRhythm >255) cityRhythm =255;
    }
    
    if ( ofGetElapsedTimeMillis()-timeLastDirection>200 && (theta>maxTheta || theta<minTheta) ) {
        direction *= -1;
        timeLastDirection = ofGetElapsedTimeMillis();
    }
    while(receiver.hasWaitingMessages()){
		// get the next message
		ofxOscMessage m;
		receiver.getNextMessage(&m);
		// check for mouse moved message
		if(m.getAddress() == "/rhythm"){
			// both the arguments are int32's
			nextCityRhythm = m.getArgAsInt32(0);
            /*
            cityRhythm_rawTwitter = m.getArgAsInt32(1);
            cityRhythm_Twitter = m.getArgAsInt32(2);
            cityRhythm_rawFlickr = m.getArgAsInt32(3);
            cityRhythm_Flickr = m.getArgAsInt32(4);
            cityRhythm_rawYoutube = m.getArgAsInt32(5);
            cityRhythm_Youtube = m.getArgAsInt32(6);
            */
            counterOSCMessages +=1;
            particleSystem.removeParticles(300);
            particleSystem.addParticles(300);
            particleSystem.addForce(ofVec2f(0, -25));

		}
    }
    /*
    // call python that grap some services online
    if(ofGetElapsedTimeMillis()-timeLastDataUpdate>60000){
        timeLastDataUpdate = ofGetElapsedTimeMillis();
        string path = ofToDataPath("python/getSaoPauloData.py", true);
        string comand = "python "+path;
        cout << comand << endl; 
        system(comand.c_str());
    }
    */
    particleSystem.update();
}

//--------------------------------------------------------------

void testApp::draw(){
    ofSetBackgroundColor(0, 0, 0,255);
    ofSetColor(0, 0, 0,255);
    ofRect(0,0,ofGetWidth(),ofGetHeight());
    ofSetColor(255, 255, 255,255);
    //base.draw(0,0);
    simulation2D();
    drawInfo();
}

//--------------------------------------------------------------

void testApp::drawInfo(){
    ofPushMatrix();
    ofTranslate(50, 50);
    ofNoFill();
    ofSetColor(255,0,0);
    ofRect(-10,-20,200,125);
    ofFill();
    ofSetColor(255,0,0);
    ofDrawBitmapString("Theta angle:"+ofToString(theta), 0,0);
    ofDrawBitmapString("Velocity:"+ofToString(velocity), 0,20);
    ofDrawBitmapString("VelocityMin:"+ofToString(velocityMin), 0,40);
    ofDrawBitmapString("CityRhythm:"+ofToString(cityRhythm), 0,60);
    ofDrawBitmapString("NextCityRhythm"+ofToString(nextCityRhythm), 0,80);
    ofDrawBitmapString("CounterOSCMessages:"+ofToString(counterOSCMessages), 0,100);
    ofPopMatrix();
}

//--------------------------------------------------------------

void testApp::setupGUI(){
    guiVisible = false;
    float dim = 32;
    float xInit = OFX_UI_GLOBAL_WIDGET_SPACING;
    float length = 320-xInit;
    gui = new ofxUICanvas(700,0,length+xInit,ofGetHeight());     
    gui->addWidgetDown(new ofxUIToggle(dim, dim, false, "FULLSCREEN")); 
    if(testColors){
        // background color
        gui->addWidgetDown(new ofxUILabel("BACKGROUND COLOR", OFX_UI_FONT_MEDIUM)); 
        gui->addSlider("RED", 0.0, 255.0,  color1.r,  (length-xInit), dim);
        gui->addSlider("GREEN", 0.0, 255.0,color1.g, (length-xInit),dim);
        gui->addSlider("BLUE", 0.0, 255.0, color1.b, (length-xInit),dim);
        // stick color
        gui->addWidgetDown(new ofxUILabel("STICK COLOR", OFX_UI_FONT_MEDIUM)); 
        gui->addSlider("RED_s", 0.0, 255.0,  color2.r,  (length-xInit), dim);
        gui->addSlider("GREEN_s", 0.0, 255.0,color2.g, (length-xInit),dim);
        gui->addSlider("BLUE_s", 0.0, 255.0, color2.b, (length-xInit),dim);
        gui->addSlider("FACTOR SPEED", 0.0, 1.0,  velocity,  (length-xInit), dim);
        gui->addSlider("MIN SPEED", 0.0, 1.0,  velocityMin,  (length-xInit), dim);
    }
    gui->addSlider("CITYRHYTHM", 0.0, 255.0, nextCityRhythm, (length-xInit),dim);
    gui->loadSettings("GUI/guiSettings.xml");   
    ofAddListener(gui->newGUIEvent,this,&testApp::guiEvent);	
}

//--------------------------------------------------------------

void testApp::guiEvent(ofxUIEventArgs &e){
    string name = e.widget->getName(); 
	int kind = e.widget->getKind();
    if(testColors){
        if(name == "RED"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            color1.r = slider->getScaledValue(); 
        }else if(name == "GREEN"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            color1.g = slider->getScaledValue(); 
        }else if(name == "BLUE"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            color1.b = slider->getScaledValue(); 		
        }if(name == "RED_s"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            color2.r = slider->getScaledValue(); 
        }else if(name == "GREEN_s"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            color2.g = slider->getScaledValue(); 
        }else if(name == "BLUE_s"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            color2.b = slider->getScaledValue(); 		
        }else if(name == "STICK WIDTH"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            stickWidth = slider->getScaledValue(); 		
        }else if(name == "B1"){
            ofxUIButton *button = (ofxUIButton *) e.widget; 
            showLines = button->getValue(); 
        }else if(name == "FACTOR SPEED"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            velocity = slider->getScaledValue(); 		
        }else if(name == "MIN SPEED"){
            ofxUISlider *slider = (ofxUISlider *) e.widget; 
            velocityMin = slider->getScaledValue(); 		
        }
    }
    
    if(name=="FULLSCREEN"){
        ofxUIButton *button = (ofxUIButton *) e.widget; 
        fullscreen = button->getValue(); 
        ofSetFullscreen(fullscreen);
    }else if(name=="CITYRHYTHM"){
        ofxUISlider *slider = (ofxUISlider *) e.widget; 
        nextCityRhythm = slider->getScaledValue();
    }
    
    
}


//--------------------------------------------------------------

void testApp::drawMetronomStick(ofFbo *_fbo,float extraTheta,float x,float y){
    _fbo->begin();  
    ofClear(255,255,255, 0);
    ofFill();
    trX = 150;
    trY = 205;
    float r = 160;
    float x1 = (r*cos(theta+extraTheta));
    float y1 = (r*sin(theta+extraTheta));
    ofVec2f vTop = ofVec2f(x1, y1);
    ofVec2f vTopPerp = vTop.getPerpendicular();
    ofVec2f vTopNorm = vTop.getNormalized();
    ofPushMatrix();
    ofFill();
    ofSetColor(color2.r,color2.g,color2.b);
    ofTranslate(trX+x,trY+y);
    // Stick
    ofBeginShape();
    ofVertex(x1+(vTopPerp.x*stickWidth),y1+(vTopPerp.y*stickWidth));
    ofVertex(x1-(vTopPerp.x*stickWidth),y1-(vTopPerp.y*stickWidth));
    ofVertex(-(vTopPerp.x*stickWidth),-(vTopPerp.y*stickWidth));
    ofVertex((vTopPerp.x*stickWidth),(vTopPerp.y*stickWidth));
    ofEndShape();
    // Metal Weight
    float metalWeightStartY = 10 + (stickHeight-180)*((float)cityRhythm/255.0f);
    int metalWeightWidth = 24;
    int metalWeightHeight = 20;
    ofVec2f topMetalPointLeft = ofVec2f(x1+(vTopPerp.x*(metalWeightWidth*0.5))-(vTopNorm.x*metalWeightStartY)
                                        ,y1+(vTopPerp.y*(metalWeightWidth*0.5))-(vTopNorm.y*metalWeightStartY));
    ofVec2f topMetalPointRight = ofVec2f(x1-(vTopPerp.x*(metalWeightWidth*0.5))-(vTopNorm.x*metalWeightStartY)
                                         ,y1-(vTopPerp.y*(metalWeightWidth*0.5))-(vTopNorm.y*metalWeightStartY));
    
    ofBeginShape();
    ofVertex(topMetalPointLeft.x,topMetalPointLeft.y);
    ofVertex(topMetalPointRight.x, topMetalPointRight.y );
    ofVertex(topMetalPointRight.x-(vTopNorm.x*metalWeightHeight)+(vTopPerp.x*(metalWeightWidth*0.25))
                                                                  , topMetalPointRight.y-(vTopNorm.y*metalWeightHeight)+(vTopPerp.y*(metalWeightWidth*0.25)));
    ofVertex(topMetalPointLeft.x-(vTopNorm.x*metalWeightHeight)-(vTopPerp.x*(metalWeightWidth*0.25))
                                                                 ,topMetalPointLeft.y-(vTopNorm.y*metalWeightHeight)-(vTopPerp.y*(metalWeightWidth*0.25)));
    ofEndShape();
    ofPopMatrix();
    _fbo->end();
}

//--------------------------------------------------------------

void testApp::drawPatternSVG(ofxSVG * svg, ofColor c){
    // Draw 
    ofFill();
    ofSetLineWidth(0);
    ofSetColor(c.r,c.g,c.b, c.a);
    for (int i = 0; i < svg->getNumPath(); i++)
    {
        ofPath &p = svg->getPathAt(i);
        vector<ofPolyline>& lines = p.getOutline();
        int totalPolyLines = lines.size();
        for (int k = 0; k < totalPolyLines; k++)
        {
            ofPolyline line = lines[k];
            int num = line.size();
            ofBeginShape();
            for (int j = 0; j < num; j++)
            {
                ofVec3f &vv = line[j];
                ofVertex(vv.x, vv.y);
                
            }
            if(num>0){
                ofVec3f &vv = line[0];
                ofVertex(vv.x, vv.y);
            }
            ofEndShape();
        }
    }
}

//--------------------------------------------------------------

void testApp::simulation2D(){

    // Draw center building
    ofPushMatrix();
    ofTranslate(99,258);
    drawPatternSVG(svgCenter,color1);
    ofPopMatrix();
    ofSetColor(255, 255, 255);
    
    // Draw left side building
    ofPushMatrix();
    ofTranslate(34,258);
    drawPatternSVG(svgLeft,color1);
    ofPopMatrix();
    
    // Draw right side building
    ofPushMatrix();
    ofTranslate(192,258);
    drawPatternSVG(svgRight,color1);
    ofPopMatrix();
    
    drawEffectDataUpdate();
    
    
    // Draw metronom details
    ofPushMatrix();
    ofTranslate(99,258);
    svgDetails->draw();
    ofPopMatrix();
    
    // Draw metronom stick
    drawMetronomStick(&fbo);
    drawMask(&fbo,&maskCenter,-3,227);
    
    drawMetronomStick(&fboLeft,-0.4,-6,-22);
    drawMask(&fboLeft,&maskLeft,-3,227);
    
    drawMetronomStick(&fboRight,0.4,+6,-22);
    drawMask(&fboRight,&maskRight,-3,227);

    // Draw lines borders building
    if(showLines){
        ofPushMatrix();
        ofTranslate(34,258);
        svgLines->draw();
        ofPopMatrix();
    }
}

//--------------------------------------------------------------


void testApp::drawEffectDataUpdate(){
    fboEffects.begin();
    ofClear(255,255,255, 0);
    particleSystem.draw();
    fboEffects.end();
    //fboEffects.draw(0,0);
    drawMask(&fboEffects,&maskAll,-3,227);
}

//--------------------------------------------------------------

void testApp::drawMask(ofFbo *_fbo,ofImage *_mask, int x, int y){
    maskShader.begin();
	maskShader.setUniformTexture("Tex0", _fbo->getTextureReference(), 0);
	maskShader.setUniformTexture("Tex1", _mask->getTextureReference(), 1);
	maskShader.end();
    
    ofEnableAlphaBlending();
    ofPushMatrix();
    ofTranslate(x, y);
    //then draw a quad for the top layer using our composite shader to set the alpha
	maskShader.begin();
	
	//our shader uses two textures, the top layer and the alpha
	//we can load two textures into a shader using the multi texture coordinate extensions
	glActiveTexture(GL_TEXTURE0_ARB);
	_fbo->getTextureReference().bind();
    
	glActiveTexture(GL_TEXTURE1_ARB);
	_mask->getTextureReference().bind();
    
	//draw a quad the size of the frame
	glBegin(GL_QUADS);
	
	//move the mask around with the mouse by modifying the texture coordinates
	float maskOffset = 0;
	glMultiTexCoord2d(GL_TEXTURE0_ARB, 0, 0);
	glMultiTexCoord2d(GL_TEXTURE1_ARB, 0, maskOffset);		
	glVertex2f( 0, 0);
    
	glMultiTexCoord2d(GL_TEXTURE0_ARB, _fbo->getWidth(), 0);
	glMultiTexCoord2d(GL_TEXTURE1_ARB, _mask->getWidth(), maskOffset);		
	glVertex2f( _mask->getWidth(), 0);
    
	glMultiTexCoord2d(GL_TEXTURE0_ARB, fbo.getWidth(), fbo.getHeight());
	glMultiTexCoord2d(GL_TEXTURE1_ARB, _mask->getWidth(), _mask->getHeight() + maskOffset);
	glVertex2f( _mask->getWidth(), _mask->getHeight());
    
	glMultiTexCoord2d(GL_TEXTURE0_ARB, 0, fbo.getHeight());
	glMultiTexCoord2d(GL_TEXTURE1_ARB, 0, _mask->getHeight() + maskOffset);		
	glVertex2f( 0, _mask->getHeight() );
	
	glEnd();
	
	//deactive and clean up
	glActiveTexture(GL_TEXTURE1_ARB);
	_mask->getTextureReference().unbind();
	
	glActiveTexture(GL_TEXTURE0_ARB);
	_fbo->getTextureReference().unbind();
	
	maskShader.end();
    ofPopMatrix();
    ofDisableAlphaBlending();
}

//--------------------------------------------------------------

void testApp::exit()
{
    gui->saveSettings("GUI/guiSettings.xml");   
	delete gui;
    delete svgLeft;
    delete svgCenter;
    delete svgRight;
}

//--------------------------------------------------------------

void testApp::keyPressed(int key){
    if(key=='l'){ 
        delete svgLeft;
        delete svgCenter;
        delete svgRight;
        svgLeft = new ofxSVG();
        svgRight = new ofxSVG();
        svgCenter = new ofxSVG();
        svgDetails = new ofxSVG();
        
        svgDetails->load("detalls.svg");
        svgLeft->load("leftSide.svg");
        svgRight->load("rightSide.svg");
        svgCenter->load("centerSide.svg");
        svgLines->load("lines.svg");
    }
    if(key==' '){ 
        cout << "press hide gui" << guiVisible << endl;
        guiVisible =!guiVisible;
        gui->setVisible(guiVisible);
    }
}

//--------------------------------------------------------------
void testApp::keyReleased(int key){

}

//--------------------------------------------------------------
void testApp::mouseMoved(int x, int y){

}

//--------------------------------------------------------------
void testApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void testApp::mousePressed(int x, int y, int button){

}

//--------------------------------------------------------------
void testApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void testApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void testApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void testApp::dragEvent(ofDragInfo dragInfo){ 

}