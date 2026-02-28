#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

double U() {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

double exponential(double rate) {
    double u = U();
    if (u == 0.0) u = 1e-12;
    return -log(1 - u) / rate;
}

int main() {
    srand(time(NULL));

    int N = 1000;
    double lambda = 2.0;  // arrivals/sec
    double mu = 1.0;      // service rate

    double arrival_time = 0.0;
    double total_service = 0.0;

    printf("ProcessID, ArrivalTime, ServiceTime\n");

    for (int i = 1; i <= N; i++) {
        double inter = exponential(lambda);
        arrival_time += inter;

        double service = exponential(mu);
        total_service += service;

        if (i <= 10) {  // print first 10 only as sample
            printf("%d, %.4f, %.4f\n", i, arrival_time, service);
        }
    }

    double avg_service = total_service / N;
    double actual_lambda = N / arrival_time;

    printf("\n--- Summary ---\n");
    printf("Total simulation time: %.4f sec\n", arrival_time);
    printf("Actual arrival rate: %.4f req/sec\n", actual_lambda);
    printf("Actual average service time: %.4f sec\n", avg_service);

    return 0;
}