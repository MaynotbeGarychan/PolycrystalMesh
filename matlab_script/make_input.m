%% Please specify your directory
ebsd_data_dir = '';
output_file_dir = '';

%% Specify Crystal and Specimen Symmetries

% crystal symmetry
CS = crystalSymmetry.load('Al-Aluminum.cif');

% specimen symmetry
SS = specimenSymmetry('triclinic');

% plotting convention
setMTEXpref('xAxisDirection','north');
setMTEXpref('zAxisDirection','outOfPlane');
setMTEXpref('FontSize',20);

%% Import the EBSD Data

% import the ebsd data

ebsd = EBSD.load(ebsd_data_dir,CS,'interface','ang','convertSpatial2EulerReferenceFrame','setting 2');

%% Reconstruct the grains

% calculate the grains
[grains,ebsd.grainId,ebsd.mis2mean] = calcGrains(ebsd('indexed'),'angle',10*degree);

% remove noise grain
ebsd(grains(grains.grainSize<20)) = [];

% segment grains again
[grains,ebsd.grainId,ebsd.mis2mean] = calcGrains(ebsd('indexed'),'angle',10*degree);

% smooth them
%grains = smooth(grains,5);

%% plot ipf map
ipf_key = ipfHSVKey(grains.CS.Laue);
ipf_key.inversePoleFigureDirection = vector3d.Z;
fig_1=figure;
ipf_color =  ipf_key.orientation2color(grains.meanOrientation);
plot(grains,ipf_color,'coordinates','on');
set(fig_1, 'Units', 'Inches', 'Position', [0, 0, 8, 8]);
hold on
%camroll(90)
% set(gca, 'YDir','reverse')
hold off

%%
odf = calcDensity(ebsd('indexed').orientations);
plotIPDF(odf, vector3d.X);

%% grain size info
% average_grainSize = mean(grains.grainSize, 'all');
% std_grainSize = std(grains.grainSize);
% fprintf(output_io,'#GRAIN_NUMBER\n');
% fprintf(output_io,'%f\n',length(grains));
% fprintf(output_io,'#GRAIN_SIZE_AVERAGE\n');
% fprintf(output_io,'%f\n',average_grainSize);
% fprintf(output_io,'#GRAIN_SIZE_STANDARDDEVIATION\n');
% fprintf(output_io,'%f\n',std_grainSize);
% fclose(output_io);

%plot pole figure of input orientation
ori = ebsd.orientations;
odf = unimodalODF(ori);
h = { ...
  Miller(1,0,0,CS),...
  Miller(1,1,0,CS),...
  Miller(1,1,1,CS),...
  };
fig_2=figure;
plotPDF(odf,h,'colorrange',[0.5,2.5],'antipodal','minmax');
setColorRange('equal') % set equal color range for all subplots
mtexColorbar % add the color bar
%hold
set(fig_2, 'Units', 'Inches', 'Position', [0, 0, 20, 5]);
hold off

%% Output important info for making mesh
% x,y,phi1,PHI,phi2,grainId
output_io = fopen(output_file_dir,'w');

% Output Point Info
fprintf(output_io,'*EBSD_POINT\n');
id_list = ebsd.id;
x_list = ebsd.x;
y_list = ebsd.y;
phi1_list = ebsd.orientations.phi1;
Phi_list = ebsd.orientations.Phi;
phi2_list = ebsd.orientations.phi2;
grainId_list = ebsd.grainId;
% Delete Useless Line
delete_row_idx = find(grainId_list==0);
id_list(delete_row_idx,:)=[];
x_list(delete_row_idx,:)=[];
y_list(delete_row_idx,:)=[];
phi1_list(delete_row_idx,:)=[];
Phi_list(delete_row_idx,:)=[];
phi2_list(delete_row_idx,:)=[];
grainId_list(delete_row_idx,:)=[];
% Output Point Info
for i=1:length(grainId_list)
    fprintf(output_io,'%d,%f,%f,%f,%f,%f,%f,%d\n',id_list(i),x_list(i),y_list(i),0.0,phi1_list(i),Phi_list(i),phi2_list(i),grainId_list(i));
end
clearvars id_list x_list y_list phi1_list Phi_list phi2_list grainId_list;

% Output Grain Info
fprintf(output_io,'*EBSD_GRAIN\n');
for i=1:length(grains)
    fprintf(output_io,'%d,%f,%f,%f\n',grains.id(i), ...
        rad2deg(grains.meanOrientation.phi1(i)),rad2deg(grains.meanOrientation.Phi(i)),rad2deg(grains.meanOrientation.phi2(i)));
end
fclose(output_io);